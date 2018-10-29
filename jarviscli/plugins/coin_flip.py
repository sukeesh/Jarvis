from plugin import plugin
import random


@plugin
def coin_flip(jarvis, s):
    """
    Randomizes between Heads and Tails
    """

    options = ('Heads', 'Tails')

    # Select a random value from the tuple
    rand_value = options[random.randint(0, 1)]

    jarvis.say(rand_value)
