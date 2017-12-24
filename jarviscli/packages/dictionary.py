from PyDictionary import PyDictionary
from utilities.GeneralUtilities import print_say
import warnings
import sys
import os
warnings.filterwarnings("ignore")


def blockPrint():
    sys.stdout = open(os.devnull, 'w')


def enablePrint():
    sys.stdout = sys.__stdout__


def dictionary(self):
    # Returns meaning, synonym and antonym of any word
    Dict = PyDictionary()
    print_say('\nEnter word', self)
    word = raw_input()
    print('\nMeaning : ' + str(Dict.googlemeaning(word)))
    blockPrint()
    syn = Dict.synonym(word)
    ant = Dict.antonym(word)
    if syn is not None:
        syn = [x.encode('UTF8') for x in syn]
    if ant is not None:
        ant = [x.encode('UTF8') for x in ant]
    enablePrint()
    print('\nSynonyms : ' + str(syn))
    print('\nAntonyms : ' + str(ant))
