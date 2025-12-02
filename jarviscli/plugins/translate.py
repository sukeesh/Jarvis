from plugin import plugin, require, alias
from googletrans import Translator
from googletrans.constants import LANGCODES, LANGUAGES, SPECIAL_CASES
import nltk
import asyncio
import os

# Split very large inputs safely (keeps sentence/line boundaries where possible)
CHUNK_LIMIT = 10000


@require(network=True)
@alias('trans')
@plugin('translate')
def translate(jarvis, s):
    """
    Translates from one language to another and allows input to be somewhat natural.

    Usage examples:
      'Jarvis, please translate, from English to French, Hello, how are you?'
      'Jarvis, could you translate Hello, how are you? from English to French for me please?'

    Also supports:
      - Auto-detect source (leave source blank / 'auto')
      - Multi-line input (each line translated, order preserved)
      - Large files: chunked automatically, asks before overwriting output
    """

    # If user typed extra parameters, try to parse a natural sentence:
    if s.strip():
        words = nltk.word_tokenize(s.lower())
        currentPos = 0
        finalPos = 0
        srcs = None
        des = None
        tex = None

        # Find source language name/code within the sentence
        for i in range(len(words)):
            word = words[i]
            currentPos = i
            # use LANGCODES (keys are names) to avoid conflicts (e.g., "hi" vs Hindi code)
            if word in LANGCODES:
                srcs = word
                break

        # Find destination language after the source language
        for i in range(currentPos + 1, len(words)):
            word = words[i]
            finalPos = i
            if word in LANGCODES:
                des = word
                break

        # If both languages were found, extract the text blob to translate
        if des and srcs:
            if currentPos < 2:
                tex = " ".join(words[finalPos + 1:])
            else:
                # Discard extra trailing words, keep the part that looks like the text
                tex = " ".join(words[:currentPos - 1])
            # Allow auto-detection
            if srcs == "" or srcs == "auto":
                srcs = "auto"
            asyncio.run(performTranslation(jarvis, srcs, des, tex))
        else:
            jarvis.say("\nSorry, I couldn't understand your translation request. Please enter the request in steps.")
            default(jarvis)
    else:
        default(jarvis)


def sentenceEnd(jarvis, t, start):
    """
    Find a nearby newline boundary (preferred over dots to avoid breaking abbreviations).
    Returns the index where a split can safely occur.
    """
    i = start
    # Guard end of string
    while i < start + 4000 and i < len(t):
        if t[i] == '\n' or t[i] == '\r\n':
            return i
        i += 1
    jarvis.say('\nCould not find a new line character in over 4000 characters. Not able to break file correctly.')
    return min(start + 4000, len(t) - 1)


def textSplitter(jarvis, t):
    """
    Split a large text blob (> CHUNK_LIMIT) into smaller parts on newline-ish boundaries.
    Returns a list of chunks.
    """
    s = []
    while len(t) > CHUNK_LIMIT:
        pivot = CHUNK_LIMIT - 4000 if CHUNK_LIMIT > 4000 else CHUNK_LIMIT // 2
        idx = sentenceEnd(jarvis, t, pivot)
        s.append(t[0:idx + 1])
        t = t[idx:len(t)]
    s.append(t[0:len(t)])
    return s


def default(jarvis):
    """
    Step-by-step interactive flow (backward compatible).
    """
    # Get source language (allow auto-detect)
    jarvis.say('\nEnter source language (or press Enter for auto-detect) ')
    srcs = jarvis.input().lower().strip() or "auto"
    # Validate source language
    while (srcs not in LANGUAGES) and (srcs not in SPECIAL_CASES) and (srcs not in LANGCODES) and (srcs != "auto"):
        if srcs in SPECIAL_CASES:
            srcs = SPECIAL_CASES[srcs]
        elif srcs in LANGCODES:
            srcs = LANGCODES[srcs]
        else:
            jarvis.say("\nInvalid source language\nEnter again (or press Enter for auto-detect)")
            srcs = jarvis.input().lower().strip() or "auto"

    # Get destination language
    jarvis.say('\nEnter destination language ')
    des = jarvis.input().lower().strip()
    # Validate destination
    while (des not in LANGUAGES) and (des not in SPECIAL_CASES) and (des not in LANGCODES):
        if des in SPECIAL_CASES:
            des = SPECIAL_CASES[des]
        elif des in LANGCODES:
            des = LANGCODES[des]
        else:
            jarvis.say("\nInvalid destination language\nEnter again")
            des = jarvis.input().lower().strip()

    jarvis.say('\nEnter text or path for file (multi-line supported)')
    tex = jarvis.input()

    asyncio.run(performTranslation(jarvis, srcs, des, tex))


async def _translate_lines_preserve_order(translator, lines, srcs, des):
    """
    Translate a list of separate lines concurrently, preserving input order.
    Returns list of tuples: (ok: bool, text: str)
    """
    tasks = []
    for line in lines:
        if not line:
            # keep blank line in place
            tasks.append(asyncio.sleep(0, result=None))
        else:
            tasks.append(translator.translate(line, src=srcs, dest=des))
    results = await asyncio.gather(*tasks, return_exceptions=True)

    ordered = []
    for line, res in zip(lines, results):
        if res is None:
            ordered.append((True, ""))  # blank line remains blank
        elif isinstance(res, Exception):
            ordered.append((False, line))  # on failure, surface original line
        else:
            ordered.append((True, getattr(res, "text", "")))
    return ordered


async def performTranslation(jarvis, srcs, des, tex):
    """
    Core translation routine with three cases:
      1) Raw text (single line): normal translate + pronunciation (if available)
      2) Raw text (multi-line): translate each line; preserve order
      3) Path to .txt file: read, and if large, chunk then translate and save
    """
    save = False
    error = False
    output_text = None

    try:
        async with Translator() as translator:
            # Case 3: file path
            if os.path.isfile(tex):
                # Only .txt files supported
                if not tex.lower().endswith(".txt"):
                    jarvis.say('\nThis is a valid path but not for a .txt file. Only txt files are supported.')
                    error = True
                else:
                    with open(tex, 'r', encoding="utf-8") as file:
                        contents = file.read()

                    # Large file → chunked translation to avoid limits
                    if len(contents) > CHUNK_LIMIT:
                        subText = textSplitter(jarvis, contents)
                        save = True
                        out_path = os.path.join(os.getcwd(), "translated.txt")
                        if os.path.exists(out_path):
                            jarvis.say(f'\nFile "{out_path}" exists. Overwrite? (yes/no)')
                            if (jarvis.input().strip().lower() or "no") != "yes":
                                jarvis.say("\nAborted saving.")
                                return
                        with open(out_path, 'w', encoding="utf-8") as f:
                            for part in subText:
                                result = await translator.translate(part, src=srcs, dest=des)
                                f.write(result.text)
                        jarvis.say('\nThe output was saved at : ' + out_path)
                    else:
                        # Small file, single call
                        result = await translator.translate(contents, src=srcs, dest=des)
                        output_text = u"""
                    [{src}] {original}
                       ->
                    [{dest}] {text}
                    """.strip().format(src=result.src, dest=result.dest, original=result.origin,
                                       text=result.text)
                        print("\n" + output_text)

            # Case 1/2: direct text
            else:
                lines = tex.splitlines()
                if len(lines) <= 1:
                    # Single line: normal path with pronunciation if available
                    result = await translator.translate(tex, src=srcs, dest=des)
                    output_text = u"""
        [{src}] {original}
           ->
        [{dest}] {text}
        [pron.] {pronunciation}
        """.strip().format(src=result.src, dest=result.dest, original=result.origin,
                           text=result.text, pronunciation=getattr(result, "pronunciation", ""))
                    print("\n" + output_text)
                else:
                    # Multi-line: keep order
                    ordered = await _translate_lines_preserve_order(translator, lines, srcs, des)
                    output_text = "\n".join([(t if ok else "") for ok, t in ordered])
                    print("\n" + output_text)

    except asyncio.TimeoutError:
        jarvis.say("\nNetwork timeout while translating. Please try again.")
        error = True
    except Exception as e:
        jarvis.say(f"\nUnexpected error while translating: {e}")
        error = True

    # Optional save to file (only for the small/printed outputs)
    if output_text is not None and not save and not error:
        jarvis.say('\nDo you want to save result to file? (yes/no)')
        ans = (jarvis.input().lower().strip() or "no")
        if ans == 'yes':
            out_path = os.path.join(os.getcwd(), "translated.txt")
            if os.path.exists(out_path):
                jarvis.say(f'\nFile "{out_path}" exists. Overwrite? (yes/no)')
                if (jarvis.input().strip().lower() or "no") != "yes":
                    jarvis.say("\nAborted saving.")
                    return
            with open(out_path, 'w', encoding="utf-8") as file:
                file.write(output_text)
            jarvis.say('\nThe output was saved at : ' + out_path)
