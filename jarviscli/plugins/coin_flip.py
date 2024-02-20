import random

from jarviscli import entrypoint

entrypoint


def coin_flip(jarvis, s):
    """
    Randomizes between Heads and Tails
    """

    options = ('Heads', 'Tails')

    rand_value = options[random.randint(0, 1)]

    jarvis.say(rand_value)
