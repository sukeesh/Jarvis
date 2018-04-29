from colorama import Fore
from six.moves import input
from aiml.brain import Brain
from utilities.GeneralUtilities import print_say


def main(self):
    brain = Brain()
    print_say("Ask me anything\n type 'leave' to stop", self, Fore.BLUE)
    stay = True

    while stay:
        text = str.upper(input(Fore.RED + ">> " + Fore.RESET))
        if text == "LEAVE":
            print_say("thanks for talking to me", self)
            stay = False
        else:
            print_say(brain.respond(text), self)
