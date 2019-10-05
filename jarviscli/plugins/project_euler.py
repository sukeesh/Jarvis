from plugin import plugin, alias, require
from colorama import Fore
import requests

@require(network=True)
@plugin('euler')
class Euler():
    def __call__(self, jarvis, s):
        jarvis.say('Welcome to the ProjectEuler plugin!', Fore.GREEN)
        jarvis.say('Please select an option below:')
        jarvis.say('')
        jarvis.say('1) Get the problem by number')
        jarvis.say('2) Get random problem')
        choice = jarvis.input_number('Your choice: ')
        
        print(choice)
