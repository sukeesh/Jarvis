from nltk.tokenize import word_tokenize as wt, sent_tokenize as st
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from collections import Counter
import nltk
import numpy as np
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk import FreqDist
import os
import requests
import json
import spacy
import random
import requests
from google_trans_new import google_translator
from difflib import SequenceMatcher

from plugin import plugin

FILE_PATH = os.path.abspath(os.path.dirname(__file__))

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


def get_text_from_news(query, apiKey):
    url = 'https://newsapi.org/v2/everything?'
    parameters = {
        'q': query,  # query phrase
        'pageSize': 100,  # maximum is 100
        'apiKey': apiKey,  # your own API key
        'language': 'en'
    }
    response = requests.get(url, params=parameters)

    # Convert the response to JSON format and pretty print it
    response_json = response.json()
    corups = []
    for i in response_json['articles']:
        corups.append(wt(i['description']))
    return corups


def word_analyzer(corpus, number, filename, title, app_id, app_key, lang, loc='', saving=True, jarvis=None):
    translate = google_translator()

    # Spacy: The following code is to remove the stop-words, recognize the lemma of the words and compute idf
    sp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])

    def get_lemma(word, sp):
        doc = sp(word)
        return doc[0].lemma_.lower(), doc[0].pos_

    def check_entity(word, sp):
        doc = sp(word)
        ent = doc.ents
        if len(ent) > 0:
            return False
        else:
            return True

    def preprocessing(corpus_words, sp):
        sp2 = spacy.load('en_core_web_sm')

        def is_not_punctuation(letter):
            try:
                return category(letter).startswith('P')
            except TypeError:
                return False

        # Reading ~5000 highly common words
        Forbidden_List = {'often': False, 'sometimes': False, 'usually': False, 'always': False,
                          'oftentimes': False, 'occasionally': False, 'regularly': False, 'frequently': False,
                          'first': False, 'second': False, 'third': False}

        with open(os.path.join(FILE_PATH, '../data/4300fullstopwords.txt'), mode='r') as f:
            for line in f:
                w = line.split()
                w = w[0]
                Forbidden_List[w.lower()] = False
        from nltk.corpus import stopwords
        from string import punctuation
        from unicodedata import category
        for w in stopwords.words('english') + list(punctuation):
            if w not in Forbidden_List:
                Forbidden_List[w] = False
        ClearedText = []
        corpus_words_dic = {}
        words = []
        clean_corpus_words = []
        for document in corpus_words:
            ClearedText = []
            for i in document:
                if i.isalpha():
                    if check_entity(i, sp2):
                        lemmatized, pos = get_lemma(i, sp)
                        if Forbidden_List.get(lemmatized, True) and not is_not_punctuation(i):
                            ClearedText.append(lemmatized)
                            words.append(lemmatized)
                            if lemmatized not in corpus_words_dic:
                                corpus_words_dic[lemmatized] = [pos]
            if len(ClearedText) > 0:
                clean_corpus_words.append(ClearedText)
        number_docs = len(clean_corpus_words)
        document_count = {}
        idfs = []
        for document in clean_corpus_words:
            word_set = np.unique(document)

            for word in word_set:
                document_count[word] = document_count.get(word, 0) + 1

        for word in document_count:
            idf = np.log(number_docs / document_count[word])
            corpus_words_dic[word].append(idf)
            idfs.append(idf)
        xarray = np.array(idfs)
        mn = np.min(xarray)
        mx = np.max(xarray)
        rng = mx - mn
        idfs = list((xarray - mn) / rng)
        for word in corpus_words_dic:
            corpus_words_dic[word][1] = ((corpus_words_dic[word][1] - mn) / rng)
        del (clean_corpus_words)
        dist = Counter(idfs)
        dist = list(dist.items())
        dist.sort(key=lambda x: x[0])
        dist = np.array(dist)
        norm = np.dot(dist.T[0], dist.T[1])
        del (idfs)
        return words, corpus_words_dic, dist, norm

    def get_word_out(word, sentence, sp):
        g = wt(sentence)
        l = [get_lemma(i, sp)[0] for i in g]
        inx = l.index(word)
        OrgWord = g[inx]
        g[inx] = '_' * len(OrgWord)
        question = " ".join([j for j in g])
        question = question + '.'
        return question, OrgWord

    def syn_ant(word):
        from nltk.corpus import wordnet
        synonyms = []
        antonyms = []
        for syn in wordnet.synsets(word):
            for l in syn.lemmas():
                synonyms.append(l.name())
                if l.antonyms():
                    antonyms.append(l.antonyms()[0].name())
        synon = ''
        ant = ''
        for i in set(synonyms):
            synon = synon + i.capitalize() + ', '
        for i in set(antonyms):
            ant = ant + i.capitalize() + ', '
        synon = synon + ' '
        synon = synon.replace(',  ', '.')
        ant = ant + ' '
        ant = ant.replace(',  ', '.')
        if synon == '  ':
            synon = 'No synonym is found for "' + word.capitalize() + '".'
        if ant == ' ':
            ant = 'No antononym is found for "' + word.capitalize() + '".'
        return synon, ant, synonyms

    def get_def_oxford(word, app_id, app_key):
        language = 'en'
        word_id = word

        url = 'https://od-api.oxforddictionaries.com:443/api/v2/entries/' + language + '/' + word_id.lower()
        # url Normalized frequency
        urlFR = 'https://od-api.oxforddictionaries.com:443/api/v2/stats/frequency/word/' + language + '/?corpus=nmc&lemma=' + word_id.lower()
        r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})

        return r, r.status_code

    words, corpus_words_dic, dist, norm = preprocessing(corpus, sp)

    f = FreqDist(words)
    WordList = f.most_common()
    idd = 0
    jarvis.say('Preprocessing Phase terminated')
    jarvis.say('Writing file is on process')
    testyourself = []
    if saving:
        f = open(loc + filename + '.txt', mode='w', newline='', encoding='UTF-8')
    if saving:
        f.write(' Javris: An Automatic Word Extraction Python Program\n')
        f.write('\n')
        f.write(' by: Nima Farnoodian and Aurélien Buchet\n')
        f.write('\n')
        f.write(' Email: nima.farnoodian@student.uclouvain.be\n')
        f.write('\n')
        f.write('\t\t\t\t\t\t\t\t\t\t' + title + '\n')
        f.write('\n')
    # Printing
    jarvis.say(' Javris: An Automatic Word Extraction Python Program\n')
    jarvis.say('\n')
    jarvis.say(' by: Nima Farnoodian and Aurélien Buchet\n')
    jarvis.say('\n')
    jarvis.say(' Email: nima.farnoodian@student.uclouvain.be\n')
    jarvis.say('\n')
    jarvis.say('\t\t\t\t\t\t\t\t\t\t' + title + '\n')
    if saving:
        f.write('\n')
    jarvis.say('\n')
    counter = 0
    number = number - 1
    if number >= len(WordList):
        number = len(WordList) - 1
    if saving:
        f.write(str(number) + ' unique Words Extracted. Enjoy your learning.\n')
        f.write('\n')
    jarvis.say(str(number) + ' unique Words Extracted. Enjoy your learning.\n')
    jarvis.say('\n')
    while counter <= number:
        i = WordList[counter]
        counter = counter + 1
        idd = idd + 1
        word = i[0]
        ferquenc = i[1]
        r, code = get_def_oxford(word, app_id, app_key)
        if code == 200:
            if saving:
                f.write(str(idd) + '. ' + word.capitalize() + '. ' + corpus_words_dic[word][0] + '. IFD=' + str(
                    corpus_words_dic[word][1]) + '. Frequency=' + str(ferquenc) + '.\n')
            jarvis.say(str(idd) + '. ' + word.capitalize() + '. ' + corpus_words_dic[word][0] + '. IFD=' + str(
                corpus_words_dic[word][1]) + '. Frequency=' + str(ferquenc) + '.\n')
            if 'etymologies' in r.json()['results'][0]['lexicalEntries'][0]['entries'][0]:
                if saving:
                    f.write('\tEtymology:\n')
                jarvis.say('\tEtymology:\n')
                for i in r.json()['results'][0]['lexicalEntries'][0]['entries'][0]['etymologies']:
                    if saving:
                        f.write('\t\t' + i.capitalize() + '.\n')
                    jarvis.say('\t\t' + i.capitalize() + '.\n')
            if 'derivatives' in r.json()['results'][0]['lexicalEntries'][0]:
                if saving:
                    f.write('\tDerivatives:\n')
                jarvis.say('\tDerivatives:\n')
                lists = ''
                for i in r.json()['results'][0]['lexicalEntries'][0]['derivatives']:
                    lists = lists + i['text'].capitalize() + ', '
                lists = lists + ' '
                lists = lists.replace(',  ', '.')
                lists = '\t\t' + lists
                if saving:
                    f.write(lists + '\n')
                jarvis.say(lists + '\n')
            TestExample = []
            try:
                if 'senses' in r.json()['results'][0]['lexicalEntries'][0]['entries'][0]:
                    if 'definitions' in r.json()['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]:
                        senses = r.json()['results'][0]['lexicalEntries'][0]['entries'][0]['senses']
                        idddd = 0
                        if len(r.json()['results'][0]['lexicalEntries'][0]['entries'][0]['senses']) == 1:
                            if saving:
                                f.write('\tDefinition:\n')
                            jarvis.say('\tDefinition:\n')
                        else:
                            if saving:
                                f.write('\tDefinitions:\n')
                            jarvis.say('\tDefinitions:\n')

                        for sens in senses:
                            idddd = idddd + 1
                            if saving:
                                f.write('\t\t' + str(idddd) + '. ' + sens['definitions'][0].capitalize() + '.\n')
                            jarvis.say('\t\t' + str(idddd) + '. ' + sens['definitions'][0].capitalize() + '.\n')

                            if 'examples' in sens:
                                if saving:
                                    f.write('\t\tExample:\n')
                                    f.write('\t\t   ' + sens['examples'][0]['text'].capitalize() + '.\n')
                                jarvis.say('\t\tExample:\n')
                                jarvis.say('\t\t   ' + sens['examples'][0]['text'].capitalize() + '.\n')
                                if len(sens['examples']) > 1:
                                    for examples in sens['examples']:
                                        TestExample.append([examples['text'].capitalize(),
                                                            sens['shortDefinitions'][0].capitalize() + '.'])
                                else:
                                    TestExample.append([sens['examples'][0]['text'].capitalize(),
                                                        sens['shortDefinitions'][0].capitalize() + '.'])
                            else:
                                continue
                        random.shuffle(TestExample)
                        TestExample = TestExample[:int(np.ceil(.3 * len(TestExample)))]
                        TestExample2 = []
                        for i in range(len(TestExample)):
                            sent = TestExample[i][0]
                            row = []
                            try:
                                q, orgw = get_word_out(word, sent, sp)
                                row.append(q)
                                row.append(TestExample[i][1])
                                row.append(orgw)
                                TestExample2.append(row)
                            except:
                                continue
                        testyourself = testyourself + TestExample2
            except:
                jarvis.say('An error appeard while finding definitions of ' + word)
                continue
            syn, ant, s = syn_ant(word)
            if syn != 'No synonym is found for "' + word.capitalize() + '".':
                if saving:
                    f.write('\tSynonyms:\n')
                    f.write('\t\t' + syn + '\n')

                jarvis.say('\tSynonyms:\n')
                jarvis.say('\t\t' + syn + '\n')

            if ant != 'No antononym is found for "' + word.capitalize() + '".':
                if saving:
                    f.write('\tAntonyms:\n')
                    f.write('\t\t' + ant + '\n')
                jarvis.say('\tAntonyms:\n')
                jarvis.say('\t\t' + ant + '\n')

    if len(testyourself) == 0:
        return
    testCheck = jarvis.input("Do you wish to test your learned vocabulary? (y/n)")
    while True:
        try:
            testLimit = int(jarvis.input("Enter a limit of exercices. "))
            break
        except ValueError:
            jarvis.say("Please enter a valid limit.")
    if testLimit >= len(testyourself):
        testLimit = len(testyourself)

    if testCheck.strip().lower() == 'y':
        userAsnwer = []
        random.shuffle(testyourself)
        if saving:
            f.write('\t\t\t\t\t\t\t\t\t\tTest Yourself\n')
            f.write('\n')
        jarvis.say('\t\t\t\t\t\t\t\t\t\tTest Yourself\n')
        jarvis.say('\n')
        ids = 0
        for i in testyourself:
            ids = ids + 1
            if ids > testLimit:
                break
            if saving:
                f.write(str(ids) + '. ' + i[0] + ' (Hint: ' + i[1] + ')\n')
            jarvis.say(str(ids) + '. ' + i[0] + ' (Hint: ' + i[1] + ')\n')
            userAsnwer.append(input("Your answer: "))
        if saving:
            f.write('\n')
            f.write('\t\t\t\t\t\t\t\t\t\tAnswer Keys\n')
            f.write('\n')
        jarvis.say('\n')
        jarvis.say('\t\t\t\t\t\t\t\t\t\tAnswer Keys\n')
        jarvis.say('\n')

        ids = 0
        correctAnswer = 0
        for i in testyourself:
            ids = ids + 1
            if ids > testLimit:
                break
            flag = False
            s = SequenceMatcher(None, userAsnwer[ids - 1].strip().lower(), i[2].strip().lower())
            if s.ratio() > .8:
                correctAnswer += 1
                flag = True
            if saving:
                f.write(str(ids) + '. Your answer: ' + userAsnwer[ids - 1] + '| Correct Answer:' + i[2] + '| ' + str(
                    flag) + '\t')
            jarvis.say(str(ids) + '. Your answer: ' + userAsnwer[ids - 1] + '| Correct Answer:' + i[2] + '| ' + str(
                flag) + '\t')
        score = correctAnswer / len(testyourself)
        if saving:
            f.write('Your score is ' + str(np.round(score, 2)) + '\n')
        jarvis.say('Your score is ' + str(np.round(score, 2)) + '\n')
    if saving:
        jarvis.say('Writing file terminated. Refer to ' + loc + filename + '.txt')


@plugin('teach me')
def call(jarvis, s):
    """
    This is an application which extracts the unique words related to a query from internet and news, then generates a .txt output file that contains the definition, etymology, example, and question about the extracted words.
    """
    jarvis.say(
        'This is an application which extracts the unique words related to a query from internet and news, then generates a .txt output file that contains the definition, etymology, example, and question about the extracted words.')
    jarvis.say(
        'Note that you need to have an oxford api-key in order to continue the process. If you do not possess the key, please refer to https://developer.oxforddictionaries.com/ to obtain your api-key.')
    apiKey = '0611eb618d244d15af619451f9d2007b'
    while (True):
        app_id = str(jarvis.input('Enter your oxford Api-ID: '))
        app_key = str(jarvis.input('Enter your oxford Api-Key: '))
        query = str(jarvis.input('Enter your query: '))
        numofwords = int(jarvis.input('Enter the maximum number of words that should be exctracted (maximum=1000)'))
        if numofwords > 1000:
            numofwords = 1000
        saving = False
        savecheck = jarvis.input("Would you like to save the results in a text file? (y/n)")
        loc = ''
        if savecheck.strip().lower() == 'y':
            loc = str(jarvis.input(
                'Enter the folder location in which the output ".txt file" will be stored (e.g. E:/Documents/Words/)'))
            saving = True
        jarvis.say('Please wait to complete the process.')
        corpus = get_text_from_news(query.lower(), apiKey)
        try:
            word_analyzer(corpus, numofwords, query.capitalize(), 'News Word Analysis for ' + query, app_id, app_key,
                          'fr', loc, saving, jarvis)
        except:
            jarvis.say(
                "An error appears. The inputs such as folder location might have been wrongly entered or maybe you don't have write access. ")
            continue
        answer = jarvis.input('Do you wish to query another word? (y/n)')
        if answer.strip().lower() != 'y':
            break
