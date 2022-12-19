from plugin import plugin
from colorama import Fore
import requests



@plugin("pokemon")
def hello_world(jarvis,s):
    if not s or 'help' in s:
        jarvis.say("pokemon name: returns the list of abilities",Fore.GREEN)
    else:
        args = s.split()
        if len(args) > 1:
            jarvis.say("pokemon name: returns the list of abilities",Fore.GREEN)
        else:
            url = 'https://pokeapi.co/api/v2/pokemon/'+args[0]
            resp = requests.get(url)

            if resp.status_code == 200:
                data = resp.json()
                jarvis.say("Abilities:")
                for element in data['abilities']:
                    jarvis.say(element['ability']['name'])
                jarvis.say("")

            else:
                jarvis.say("This pokemon does not exist.",Fore.RED)


                