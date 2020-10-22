import random
import re

import requests
from colorama import Fore

from plugin import plugin, require


def parse_species_data(poke_data):
    """ Parse and construct text for Jarvis to say about a Pokemon species.

        :param poke_data: dict containing information about a Pokemon species.
    """
    template = '{}\nGeneration: {}\nLegendary? {}\nMythical? {}\nDescription: {}\n'

    # Regex to clean description text
    regex = re.compile(r'[\n\r\t\x0c\xad]')

    # Parse pokemon species data
    name = poke_data['name']
    gen = poke_data['generation']['name']
    is_legendary = 'Yes' if poke_data['is_legendary'] else 'No'
    is_mythical = 'Yes' if poke_data['is_mythical'] else 'No'

    # Get random description text (English only)
    # TODO: not just English text
    flavor_texts = [ft for ft in poke_data['flavor_text_entries'] if ft['language']['name'] == 'en']
    try:
        description = random.choice(flavor_texts)['flavor_text']
    except IndexError:
        description = "No description found."

    return template.format(name.title(), gen.title(), is_legendary, is_mythical, regex.sub(' ', description))


@require(network=True)
@plugin('pokemon')
def pokemon(jarvis, s):
    """ Get information about a Pokemon species.

        Utilizes PokeApi to obtain the information: https://pokeapi.co/
    """
    if not s:
        jarvis.say('Tell me the name of the pokemon you want to know more about :)\n', Fore.YELLOW)
        return

    res = requests.get(f'https://pokeapi.co/api/v2/pokemon-species/{s.lower()}/')

    if res.ok:
        try:
            poke_data = res.json()
            poke_text = parse_species_data(poke_data)
            jarvis.say(poke_text, Fore.BLUE)
        except (ValueError, KeyError):
            jarvis.say('Something went wrong. Please try again later.\n', Fore.RED)
    else:
        jarvis.say(f'Could not retrieve info about {s}.\n', Fore.RED)
