import numpy
import nltk
from plugin import plugin
from nltk import word_tokenize, sent_tokenize
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

@plugin("text analysis")
def text_analysis(jarvis, s):

    sentence = jarvis.input("Write down the text: ")
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    entities = nltk.chunk.ne_chunk(tagged)
    print('Analysis result: ')
    print(entities)
