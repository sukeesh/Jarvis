#!/home/saurabh/jarvis/Jarvis/env/bin/python2.7

from __future__ import print_function
from gtts import gTTS
from gtts import __version__
import sys
import argparse
import os
import codecs

def languages():
    """Sorted pretty printed string of supported languages"""
    return ", ".join(sorted("{}: '{}'".format(gTTS.LANGUAGES[k], k) for k in gTTS.LANGUAGES))

# Args
desc = "Creates an mp3 file from spoken text via the Google Text-to-Speech API ({v})".format(v=__version__)
parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)

text_group = parser.add_mutually_exclusive_group(required=True)
text_group.add_argument('text', nargs='?', help="text to speak")      
text_group.add_argument('-f', '--file', help="file to speak")

parser.add_argument("-o", '--destination', help="destination mp3 file", action='store')
parser.add_argument('-l', '--lang', default='en', help="ISO 639-1/IETF language tag to speak in:\n" + languages())
parser.add_argument('--debug', default=False, action="store_true")

args = parser.parse_args()

try:
    if args.text:
        if args.text == "-":
            text = sys.stdin.read()
        else:
            text = args.text
    else:
        with codecs.open(args.file, "r", "utf-8") as f:
            text = f.read()

    # TTSTF (Text to Speech to File)
    tts = gTTS(text=text, lang=args.lang, debug=args.debug)

    if args.destination:
        tts.save(args.destination)
    else:
        tts.write_to_fp(os.fdopen(sys.stdout.fileno(), "wb"))

except Exception as e:
    if args.destination:
        print(str(e))
    else:
        print("ERROR: ", e, file=sys.stderr)
        
