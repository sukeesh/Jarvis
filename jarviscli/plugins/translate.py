from googletrans import Translator
from utilities.GeneralUtilities import print_say
from googletrans.constants import LANGCODES, LANGUAGES, SPECIAL_CASES
from six.moves import input


def main(self):

    '''
        source language
    '''

    print_say('\nEnter source language ', self)
    srcs = input()
    while (srcs not in LANGUAGES) and (srcs not in SPECIAL_CASES) and (srcs not in LANGCODES):
        if srcs in SPECIAL_CASES:
            srcs = SPECIAL_CASES[srcs]
        elif srcs in LANGCODES:
            srcs = LANGCODES[srcs]
        else:
            print_say("\nInvalid source language\nEnter again", self)
            srcs = input()
    print_say('\nEnter destination language ', self)
    des = input()
    while (des not in LANGUAGES) and (des not in SPECIAL_CASES) and (des not in LANGCODES):
        if des in SPECIAL_CASES:
            des = SPECIAL_CASES[des]
        elif des in LANGCODES:
            des = LANGCODES[des]
        else:
            print_say("\nInvalid destination language\nEnter again", self)
            des = input()
    print_say('\nEnter text ', self)
    tex = input()
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
