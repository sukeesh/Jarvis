from plugin import plugin, PYTHON2

from colorama import Fore
from six.moves import input


@plugin(python=PYTHON2)
def ask(jarvis, s):
    """Start chating with Jarvis"""
    from aiml.brain import Brain

    brain = Brain()
    jarvis.say("Ask me anything\n type 'leave' to stop", self, Fore.BLUE)
    stay = True

    while stay:
        text = str.upper(input(Fore.RED + ">> " + Fore.RESET))
        if text == "LEAVE":
            jarvis.say("thanks for talking to me", self)
            stay = False
        else:
            jarvis.say(brain.respond(text), self)
