from PyDictionary import PyDictionary 
from plugin import plugin, require

@require(network=True)
@plugin("synonyms of")
def synonyms(jarvis, s):
    """
    Returns synonyms of a given word
    """
    if s == "":
        s = jarvis.input("Enter word \n")

    dictionary = PyDictionary() 
    word = s.lower().strip()
    synonyms = dictionary.synonym(word)
    if synonyms:
        synonym_string = ', '.join(synonyms[:5])
        jarvis.say(synonym_string)
