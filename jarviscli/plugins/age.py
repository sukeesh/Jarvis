import re

import requests
from colorama import Fore
from jarviscli import entrypoint


def fetch(name):
    url = 'https://api.agify.io?name='
    r = requests.get(url + name)
    r = r.json()
    if "errorCode" in r.keys():
        return None
    return r


def get_name(jarvis):
    # Ask for the name
    print()
    while True:
        name = str(jarvis.input("Give a name: ", Fore.BLUE))
        return name


@entrypoint
def age(jarvis, s):
    name = get_name(jarvis)
    name = re.sub("[^A-Za-z]", "", name)

    if name is None:
        return

        r = fetch((str(name)))
        print("The average age for this name is "+str(r["age"]))
        print()
