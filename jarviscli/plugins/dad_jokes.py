import requests
from jarviscli import entrypoint

"""
Tells a random dad joke from https://icanhazdadjoke.com
"""


@entrypoint
def dadjoke(self, jarvis, s):
    """
    Tells a Dad Joke every time you type one of the aliases:
        1) Tell me a dad joke
        2) dad joke
        3) dadjoke
    """

    api_url = 'https://icanhazdadjoke.com'
    header = {'Accept': 'application/json'}
    r = requests.get(api_url, headers=header)

    jarvis.say(r.json()['joke'])
