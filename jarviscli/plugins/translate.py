from plugin import plugin, require, alias
from googletrans import Translator
from googletrans.constants import LANGCODES, LANGUAGES, SPECIAL_CASES
import nltk
import asyncio
import os


@require(network=True)
@alias('trans')
@plugin('translate')
def translate(jarvis, s):
    """
    Translates from one language to another and allows input to be somewhat natural.

    Usage:

    'Jarvis, please translate, from English to French, Hello, how are you?'

    OR

    'Jarvis, could you translate Hello, how are you? from English to French for me please?'
    """

    #   Check whether user has entered translate by itself or with extra parameters
    if s != "":
        words = nltk.word_tokenize(s.lower())
        currentPos = 0
        finalPos = 0
        srcs = None
        des = None

        #       Search input string for source language
        for i in range(len(words)):
            word = words[i]
            currentPos = i

            #           Do not include lang codes in the tests when using full sentence command since words can conflict with them (Eg. hi -> Hindi).
            #           This code looks like it includes them, but since the googletrans API is implemented such that the languages are stored in
            #           dictionaries, when the "in" operator is used, it only checks the keys of the dictionary, not the values. Therefore, the
            #           LANG_CODES dictionary must be used to check full language names instead of the LANGUAGES dictionary. For more clarification,
            #           have a look at the code on the googletrans github.
            if (word in LANGCODES):
                srcs = word
                break

        #       Search input string for destination language starting from the word after the source language
        for i in range(currentPos + 1, len(words)):
            word = words[i]
            finalPos = i
            #           Do not include LANGCODES in the tests when using full sentence command since words can conflict with them (Eg. hi -> Hindi)
            if (word in LANGCODES):
                des = word
                break

        #       If both languages found, work out where the text to be translated is in the sentence and perform the translation
        if (des and srcs):
            if (currentPos < 2):
                tex = " ".join(words[finalPos + 1:])
            else:
                tex = " ".join(words[:currentPos - 1])  # Discards extra words at the end of the sentence
            performTranslation(jarvis, srcs, des, tex)
        #       Otherwise perform the default method for translation
        else:
            jarvis.say("\nSorry, I couldn't understand your translation request. Please enter the request in steps.")
            default(jarvis)
    else:
        default(jarvis)


def sentenceEnd(jarvis, t, start):
    """
    Checks for new line characters '\n or \r\n' that would mean the end of sentence.

    This work better that trying to find dots (.) because it can break semantic continuity
    with cases like " J. Doe, e.g. ". Returns the index where end of sentence is found.
    """
    i = start
    while i < start + 4000:
        # Checks for new line characters
        if t[i] == '\n' or t[i] == '\r\n':
            return i
        i += 1
    jarvis.say('\nCould not find a new line character in over 4000 characters. Not able to break file correctly.')
    return i


def textSplitter(jarvis, t):
    """
    Splits the file text (larger than 10k characters) in smaller parts
    returns a list with the smaller parts
    """
    s = []
    while len(t) > 10000:
        idx = sentenceEnd(jarvis, t, 6000)
        s.append(t[0:idx + 1])
        t = t[idx:len(t)]
    s.append(t[0:len(t)])
    return s


def default(jarvis):
    """
    Default function that is called when translate is entered alone or
    when input is not understood when translate is entered with additional parameters
    """
    #   Get source language
    jarvis.say('\nEnter source language ')
    srcs = jarvis.input().lower().strip()
    #   Check source language
    while (
            srcs not in LANGUAGES) and (
            srcs not in SPECIAL_CASES) and (
            srcs not in LANGCODES) and not srcs == "auto":
        if srcs in SPECIAL_CASES:
            srcs = SPECIAL_CASES[srcs]
        elif srcs in LANGCODES:
            srcs = LANGCODES[srcs]
        else:
            jarvis.say("\nInvalid source language\nEnter again")
            srcs = jarvis.input().lower()
    #   Get destination language
    jarvis.say('\nEnter destination language ')
    des = jarvis.input().lower().strip()
    #   Check destination language
    while (
            des not in LANGUAGES) and (
            des not in SPECIAL_CASES) and (
            des not in LANGCODES):
        if des in SPECIAL_CASES:
            des = SPECIAL_CASES[des]
        elif des in LANGCODES:
            des = LANGCODES[des]
        else:
            jarvis.say("\nInvalid destination language\nEnter again")
            des = jarvis.input().lower()

    jarvis.say('\nEnter text or path for file')
    tex = jarvis.input()

    asyncio.run(performTranslation(jarvis, srcs, des, tex))


async def performTranslation(jarvis, srcs, des, tex):
    """
    Function that performs the actual translation give the user input
    There are 3 cases :
    1. input is text.

    2. input is a small txt file ( less than 10k characters )
    able to be translated with one call to the library.

    3. Large txt files that need to be broken up to smaller chunks.

    In cases 1 and 2 the output is printed in the screen
    with the option to save the output to a file at the current working directory.
    while in case 3 the output is too large and would clutter the terminal
    window, so it is only saved to the file by default.
    """
    save = False
    error = False
    async with Translator() as translator:
        # Checks if the input is a valid path
        if os.path.isfile(tex):
            # Checks if the file is a txt file
            if not tex[len(tex) - 3: len(tex)] == "txt":
                jarvis.say('\nThis is a valid path but not for a .txt file. Only txt files are supported.')
                error = True
            else:
                with open(tex, 'r') as file:
                    tex = file.read()
                # Case of a file with more that 10k characters
                # Breaks the text into smaller parts
                # translates one by one and saves the output to a file
                if len(tex) > 10000:
                    subText = textSplitter(jarvis, tex)
                    save = True
                    f = open("./translated.txt", 'w', encoding="utf-8")
                    for i in range(len(subText)):
                        result = await translator.translate(subText[i], src=srcs, dest=des)
                        f.write(result.text)
                    f.close()
                    jarvis.say('\nThe output was saved at : ' + os.getcwd() + '\\' + "translated.txt")
                # Small file able to be translated with a single call of the translation API
                else:
                    result = await translator.translate(tex, src=srcs, dest=des)
                    result = u"""
                    [{src}] {original}
                       ->
                    [{dest}] {text}
                    """.strip().format(src=result.src, dest=result.dest, original=result.origin,
                                       text=result.text)
                    print("\n" + result)
        # Case where input is text and not a file
        else:
            result = await translator.translate(tex, src=srcs, dest=des)
            result = u"""
        [{src}] {original}
           ->
        [{dest}] {text}
        [pron.] {pronunciation}
        """.strip().format(src=result.src, dest=result.dest, original=result.origin,
                           text=result.text, pronunciation=result.pronunciation)
            print("\n" + result)
        # Optional save to file function
        # Maybe we can add saving to specif path but this requires more user input
        if not save and not error:
            jarvis.say('\n Do you want to save result to file?')
            ans = jarvis.input().lower().strip()
            if ans == 'yes':
                with open("./translated.txt", 'w', encoding="utf-8") as file:
                    file.write(result)
                jarvis.say('\nThe output was saved at : ' + os.getcwd() + '\\' + "translated.txt")
