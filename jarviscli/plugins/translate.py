from plugin import plugin, require
from googletrans import Translator
from googletrans.constants import LANGCODES, LANGUAGES, SPECIAL_CASES


@require(network=True)
@plugin('translate')
def translate(jarvis, s):
    """
    translates from one language to another.
    """

    jarvis.say('\nEnter source language ')
    srcs = jarvis.input().lower().strip()
    while (
        srcs not in LANGUAGES) and (
        srcs not in SPECIAL_CASES) and (
            srcs not in LANGCODES):
        if srcs in SPECIAL_CASES:
            srcs = SPECIAL_CASES[srcs]
        elif srcs in LANGCODES:
            srcs = LANGCODES[srcs]
        else:
            jarvis.say("\nInvalid source language\nEnter again")
            srcs = jarvis.input().lower()
    jarvis.say('\nEnter destination language ')
    des = jarvis.input().lower().strip()
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
    jarvis.say('\nEnter text ')
    tex = jarvis.input()
    translator = Translator()
    result = translator.translate(tex, dest=des, src=srcs)
    result = u"""
[{src}] {original}
    ->
[{dest}] {text}
[pron.] {pronunciation}
    """.strip().format(src=result.src, dest=result.dest, original=result.origin,
                       text=result.text, pronunciation=result.pronunciation)
    print(result)
