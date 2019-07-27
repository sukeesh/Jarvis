import numpy
import nltk
from plugin import plugin
from nltk import word_tokenize, sent_tokenize


@plugin("text analysis")
def text_analysis(jarvis, s):
    """
    Basic functionallity for a NLTK system.
    Just write a string and the script will give you the entities that it can find
    """
    sentence = jarvis.input("Write down the text: ")
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    entities = nltk.chunk.ne_chunk(tagged)
    print('Analysis result: ')
    print(entities)
