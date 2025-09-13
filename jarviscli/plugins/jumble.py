import os
from plugin import plugin


@plugin("jumble")
class Jumble():
    def __call__(self, jarvis, s):
        data_path = os.path.abspath(os.path.dirname(__file__))
        data = data_path[:-8] + '/data/words'
        dict = {}
        file = open(data, "r")
        for word in file:
            word = word.strip().lower()
            sorted_word = ''.join(sorted(word))
            if sorted_word in dict:
                if word not in dict[sorted_word]:
                    dict[sorted_word].append(word)
            else:
                dict[sorted_word] = [word]
        while (True):
            jumble = jarvis.input(
                "Enter a jumble to solve or 'quit' to quit:\n")
            jumble = jumble.lower()
            if (jumble == "quit"):
                break
            jumble = ''.join(sorted(jumble))
            if jumble in dict:
                results = dict[jumble]
                for result in results:
                    jarvis.say(result + '\n')
            else:
                jarvis.say("Result not found")
