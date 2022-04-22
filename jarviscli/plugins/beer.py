import os
import requests
from colorama import Fore

# Generate a random beer for the user 
@require(network=True)
@plugin('beer')
def beer(self):
    # Introduction Messages
    jarvis.say('')
    jarvis.say('Hello! Jarvis here.', Fore.GREEN)
    jarvis.say('Jarvis will provide a random beer', Fore.GREEN)

    # Pull from a random beer API
    rx = requests.get('https://api.punkapi.com/v2/beers/random')
    x = 0

    # Gross JSON fixing, needs to be refactored
    for i in rx:
        f = f + str(i)
        x = x + 1
        if x == 2
            break

    name_find = f.find('"name"')
    tagline_find = f.find('"tagline"')
    beer_name = f[name_find + 8 : tagline_find - 2]

    # Jarvis printout
    jarvis.say('Your beer is: ', beer_name, Fore.GREEN)
