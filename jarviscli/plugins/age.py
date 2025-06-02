import requests
from colorama import Fore
from plugin import plugin, require
import re

def fetch(name):
    
    url = 'https://api.agify.io?name='
    r = requests.get(url + name)
    r = r.json()
    if "errorCode" in r.keys():
        return None
    return r

@require(network=True)
@plugin('age')
class Age():
    
    def __call__(self, jarvis, s):
        name = self.get_name(jarvis)
        name = re.sub("[^A-Za-z]", "", name)

        if name is None:
            return
        
        r = fetch((str(name)))
        print("The average age for this name is "+str(r["age"]))
        print()        
        
    def get_name(self, jarvis):
        # Ask for the name
        print()
        while True:
            name = str(jarvis.input("Give a name: ", Fore.BLUE))
            return name
        
