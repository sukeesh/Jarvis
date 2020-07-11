from PyDictionary import PyDictionary 
from plugin import plugin, require

@require(network=True)
@plugin("antonyms of")
def antonyms(jarvis, s):
    """
    Returns antonyms of a given word
    """
    if s == "":
        s = jarvis.input("Enter word \n")

    dictionary = PyDictionary() 
    word = s.lower().strip()
    antonyms = dictionary.antonym(word)
    if antonyms:
        antonym_string = ', '.join(antonyms[:5])
        jarvis.say(antonym_string)
