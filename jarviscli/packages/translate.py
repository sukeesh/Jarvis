from googletrans import Translator
from utilities.GeneralUtilities import print_say
from googletrans.constants import LANGCODES, LANGUAGES, SPECIAL_CASES


def main(self):

    '''
        source language
    '''

    print_say('\nEnter source language ', self)
    srcs = raw_input()
    while (srcs not in LANGUAGES) and (srcs not in SPECIAL_CASES) and (srcs not in LANGCODES):
        if srcs in SPECIAL_CASES:
            srcs = SPECIAL_CASES[srcs]
        elif srcs in LANGCODES:
            srcs = LANGCODES[srcs]
        else:
            print_say("\nInvalid source language\nEnter again", self)
            srcs = raw_input()

    '''
        destination language
    '''

    print_say('\nEnter destination language ', self)
    des = raw_input()
    while (des not in LANGUAGES) and (des not in SPECIAL_CASES) and (des not in LANGCODES):
        if des in SPECIAL_CASES:
            des = SPECIAL_CASES[des]
        elif des in LANGCODES:
            des = LANGCODES[des]
        else:
            print_say("\nInvalid destination language\nEnter again", self)
            des = raw_input()

    '''
        text to be translated
    '''

    print_say('\nEnter text ', self)
    tex = raw_input()
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
