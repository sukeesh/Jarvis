import pyjokes
from colorama import Fore
from jarviscli import entrypoint


@entrypoint
def joke(jarvis, s):
    """Tells a random joke"""
    joke = pyjokes.get_joke()

    jarvis.say(joke, Fore.BLUE)
