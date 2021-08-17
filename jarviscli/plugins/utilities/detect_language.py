import contextlib
import json
import os

from colorama import Fore

import fasttext
from plugin import plugin

FILE_PATH = os.path.abspath(os.path.dirname(__file__))


@plugin("detect lang")
def detect_language(jarvis, s):
    """
    Detects the language of an input string
    """

    while s == "":
        s = jarvis.input("Enter text \n")

    model = open_model()
    output = model.predict(s)
    generate_response(jarvis, output)


def generate_response(jarvis, output):
    """
    Generates response based on the probability of a predicted language
    """
    score = output[1][0]
    label = output[0][0]
    code_to_lang = open_languages()
    lang_code = label.split('_')[-1]
    language = code_to_lang[lang_code]
    if score > 0.5:
        jarvis.say('The language of the text is ' + language, Fore.GREEN)
    elif score > 0.25:
        jarvis.say("I'm not sure, but the language might be " + language, Fore.YELLOW)
    else:
        jarvis.say("I couldn't identify the language", Fore.BLUE)


def open_model():
    """
    Opens a language detector model and disables warnings
    """
    model_path = os.path.join(FILE_PATH, "../data/lid.176.ftz")
    fasttext.FastText.eprint = print
    with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
        model = fasttext.load_model(model_path)
    return model


def open_languages():
    """
    Opens a dictionary from code to its corresponding language
    """
    language_path = os.path.join(FILE_PATH, "../data/code_to_lang.json")
    with open(language_path, 'r') as f:
        languages = json.load(f)
    return languages
