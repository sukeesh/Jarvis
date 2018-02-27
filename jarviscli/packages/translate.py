from googletrans import Translator
from utilities.GeneralUtilities import print_say
from googletrans.constants import LANGCODES, LANGUAGES, SPECIAL_CASES
import six

def main(self):
    """ translates a sentance """

    def get_input():
        """ reads input from stdin
            implementation differ on whether python2 or python3 is used
        """
        if six.PY2:
            return raw_input()
        else:
            return input()

    # make the user provide a source language
    print_say('\nEnter source language ', self)
    srcs = get_input()
    while (srcs not in LANGUAGES) and (srcs not in SPECIAL_CASES) and (srcs not in LANGCODES):
        print_say("\nInvalid source language\nEnter again", self)
        srcs = get_input()

    # make the user provide a 'destination' language
    print_say('\nEnter destination language ', self)
    des = get_input()
    while (des not in LANGUAGES) and (des not in SPECIAL_CASES) and (des not in LANGCODES):
        print_say("\nInvalid destination language\nEnter again", self)
        des = get_input()

    # make the user provide a sentence to translate
    print_say('\nEnter text ', self)
    text = get_input()
    translator = Translator()
    result = translator.translate(text, dest=des, src=srcs)

    output_lines = [
        u'[{src}] {original}',
        u'    ->',
        u'[{dest}] {text}',
        u'[pron.] {pronunciation}'
    ]

    result = '\n'.join(output_lines).strip().format(
        src=result.src,
        dest=result.dest,
        original=result.origin,
        text=result.text,
        pronunciation=result.pronunciation
    )

    print(result)
