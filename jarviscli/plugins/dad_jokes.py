import requests
from plugin import plugin, require, alias

"""
Tells a random dad joke from https://icanhazdadjoke.com
"""


@alias('Tell me a dad joke', 'dad joke')
@require(network=True)
@plugin('dadjoke')
class dad_joke:
    """
    Tells a Dad Joke every time you type one of the aliases:
        1) Tell me a dad joke
        2) dad joke
        3) dadjoke
    """

    def __call__(self, jarvis, s):
        api_url = 'https://icanhazdadjoke.com'
        header = {'Accept': 'application/json'}
        r = requests.get(api_url, headers=header)

        jarvis.say(r.json()['joke'])