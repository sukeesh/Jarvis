from plugin import plugin, alias, require
from colorama import Fore
import requests

@require(network=True)
@plugin('euler')
class Euler():
    def __call__(self, jarvis, s):
        jarvis.say('Euler')
