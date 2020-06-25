import os
import random
from colorama import Fore, Back, Style
import webbrowser
import time
from plugin import plugin


FILE_PATH = os.path.abspath(os.path.dirname(__file__))


def read_questions():
    Q = []
    with open(os.path.join(FILE_PATH,
                           "../data/personality_questions.tsv")) as f:
        for i, line in enumerate(f):
            Q.append([i + 1] + line.strip().split('\t'))
    return Q


@plugin("personality")
class personality_test:
    """
    Runs Personality test
    Taken from: https://openpsychometrics.org/tests/OJTS/development/#liscmark
     Test is licensed under Creative Commons
     Attribution-NonCommercial-ShareAlike 4.0
     International License.
    """

    def __init__(self):
        self.Q = read_questions()
        self.answers = {}
        self.instruction = Back.YELLOW + "There are a total of " +\
            "32 pairs of descriptions. For each pair, choose on a scale of " +\
            "1-5. Choose 1 if you are all the way to the left, and choose " +\
            "3 if you are in the middle, etc." + Style.RESET_ALL

        self.types = ['IE', 'SN', 'FT', 'JP']
        self.scoring_scheme = ((30, (15, 23, 27), (3, 7, 11, 19, 31)),
                               (12, (4, 8, 12, 16, 20, 32), (24, 28)),
                               (30, (6, 10, 22), (2, 14, 18, 26, 30)),
                               (18, (1, 5, 13, 21, 29), (9, 17, 25)))

        self.scores = []
        self.type = []

    def get_scores(self):
        for i, personality_type in enumerate(self.types):
            score = self.scoring_scheme[i][0]
            for Q_id in self.scoring_scheme[i][1]:
                score += self.answers[Q_id]
            for Q_id in self.scoring_scheme[i][2]:
                score -= self.answers[Q_id]

            self.scores.append(score)
            if score <= 24:
                self.type.append(personality_type[0])
            else:
                self.type.append(personality_type[1])
        self.type = ''.join(self.type)

    def open_analysis(self):
        url = "https://www.16personalities.com/{}-personality"
        webbrowser.open_new(url.format(self.type.lower()))

    def __call__(self, jarvis, s):
        prompt = "{black}Q{Q_id} {cyan}{left} {black}--- {green}{right}"
        prompt_formatter = {
            'cyan': Fore.CYAN,
            'black': Fore.BLACK,
            'green': Fore.GREEN
        }
        jarvis.say("Start personality test..", color=Fore.BLACK)
        jarvis.say(self.instruction)
        for i, (Q_id, left, right) in enumerate(self.Q):
            prompt_formatter['Q_id'] = i
            prompt_formatter['left'] = left
            prompt_formatter['right'] = right

            jarvis.say(prompt.format(**prompt_formatter))
            user_input = jarvis.input_number(
                prompt="Enter your choice on the scale of 1-5:\n", rmin=1,
                rmax=5, color=Fore.BLUE, rtype=int)
            self.answers[Q_id] = user_input
        self.get_scores()

        jarvis.say(
            "{}Your personality is: {}{}{}{}".format(
                Fore.BLUE,
                Fore.BLACK,
                Back.MAGENTA,
                self.type,
                Style.RESET_ALL))
        jarvis.say(
            "Redirecting to your personality analysis\
                 in 3s...", color=Fore.BLUE)
        time.sleep(3)
        self.open_analysis()
