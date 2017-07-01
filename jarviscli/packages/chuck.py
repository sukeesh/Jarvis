from colorama import Fore
from utilities.GeneralUtilities import print_say
import requests


def main(self):
    try:
        req = requests.get("https://api.chucknorris.io/jokes/random")
        chuck_json = req.json()

        chuck_fact = chuck_json["value"]
        print_say(chuck_fact, self, Fore.RED)
    except:
        print_say("Looks like Chuck broke the Internet...", self, Fore.RED)
