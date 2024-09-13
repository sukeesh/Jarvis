import requests
from plugin import plugin, require
from colorama import Fore
from packages.memory.memory import Memory

URL = "API_URL"
API_KEY = "API_KEY"

@require(network=True)
@plugin("soccer")
class soccer():
