import requests
from colorama import Fore
from plugin import plugin, require

@plugin("nationalize")
def nationalize(jarvis, s):
    """Tells the nationality of someone based on his name"""

    req = requests.get("https://api.nationalize.io?name=" + s)
    data = req.json()
    response ="There are "

    for nationality in data.get('country'):
        req = requests.get("https://restcountries.eu/rest/v2/alpha/" + nationality.get('country_id').lower())
        country = req.json()
        response += str(round(nationality.get('probability') * 100)) + "% chances that you are from " + country.get("name") + ",\n"

    jarvis.say(response, Fore.BLUE)
