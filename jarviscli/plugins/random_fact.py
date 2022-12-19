from plugin import plugin
from colorama import Fore
import requests



@plugin("fact")
def hello_world(jarvis,s):
    url = 'https://uselessfacts.jsph.pl/random.json?language=en'
    resp = requests.get(url)

    if resp.status_code == 200:
        data = resp.json()
        jarvis.say(data['text'])

    else:
        jarvis.say("No fact was encountered",Fore.RED)


                