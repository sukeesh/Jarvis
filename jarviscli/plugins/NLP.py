import spacy

from plugin import plugin

@plugin("NLP")
class NLP:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
