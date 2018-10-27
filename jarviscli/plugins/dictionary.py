from plugin import plugin
from six.moves import input
from nltk.corpus import wordnet
import nltk


nltk.data.path.append("jarviscli/data/ntlk")


@plugin()
def dictionary(jarvis, s):
    """
    Get meaning, synonym and antonym of any word
    """
    if len(s) == 0:
        jarvis.say('\nEnter word')
        word = input()
    else:
        word = s

    syns = wordnet.synsets(word)
    if len(syns) == 0:
        jarvis.say("Don't recognise that word")
        return

    synonyms = set()
    antonyms = set()

    count = 0
    for meaning in syns:
        count = count + 1
        jarvis.say("{:>3}. {}".format(count, meaning.definition()))

        for synonym in meaning.lemmas():
            if synonym.name() != word:
                synonyms.add(synonym.name())
            for antonym in synonym.antonyms():
                antonyms.add(antonym.name())

    jarvis.say('\nSynonyms:\n' + ", ".join(synonyms))
    jarvis.say('\nAntonyms:\n' + ", ".join(antonyms))

    # detail loop
    def input_detail_id():
        jarvis.say("")
        synlen = len(syns)
        detail_id = input("Details of meaning (1-{}): ? ".format(synlen))
        if detail_id == '':
            return None

        try:
            detail_id = int(detail_id)
        except ValueError:
            return input_detail_id()

        if detail_id <= 0 or detail_id > synlen:
            jarvis.say("Choose Value between 1 and {}".format(synlen))
            return input_detail_id()

        return detail_id

    detail_id = input_detail_id()
    while detail_id is not None:
        meaning = syns[detail_id - 1]

        synonyms = [synonym for synonym in meaning.lemma_names() if synonym != word]
        examples = meaning.examples()

        antonyms = set()
        for synonym in meaning.lemmas():
            for antonym in synonym.antonyms():
                antonyms.add(antonym.name())

        jarvis.say('')
        jarvis.say('== {}. =='.format(detail_id))
        jarvis.say("Meaning  : {}".format(meaning.definition()))
        if len(synonyms) > 0:
            jarvis.say("Synonyms : {}".format(", ".join(synonyms)))
        if len(antonyms) > 0:
            jarvis.say("Antonyms : {}".format(", ".join(antonyms)))
        if len(examples) > 0:
            if len(examples) == 1:
                jarvis.say("Examples : {}".format(examples[0]))
            else:
                jarvis.say("Examples :\n-{}".format("\n- ".join(examples)))

        detail_id = input_detail_id()
