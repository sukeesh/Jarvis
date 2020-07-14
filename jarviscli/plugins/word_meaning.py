from PyDictionary import PyDictionary 
from plugin import plugin, require
from colorama import Fore


@require(network=True)
@plugin("meaning of")
def get_meaning(jarvis, s):
    """
    Returns meaning of a given word
    """
    if s == "":
        s = jarvis.input("Enter word \n")

    dictionary = PyDictionary() 
    word = s.lower().strip()
    meaning = dictionary.meaning(word, disable_errors=True)
    if meaning:
        for part, explanations in meaning.items():
            jarvis.say(part, Fore.GREEN)
            for num, text in enumerate(explanations):
                full_string = str(num+1) + ') ' + text 
                jarvis.say(full_string)
    else:
        jarvis.say("I couldn't find meaning of " + s)

