from plugin import plugin
from colorama import Fore
import requests

@plugin("generate_password")

def generate_password(jarvis, s):
    length = int(jarvis.input("Desire password length: "))
    inp = str(jarvis.input("Would you like to exclude numbers? (Y/N) : "))
    if(inp == 'Y'):
        exclude_numbers = True
    else:
        exclude_numbers = False

    inp = bool(jarvis.input("Would you like to exclude special characters? (Y/N) : "))
    if(inp == 'Y'):
        exclude_special = True
    else:
        exclude_special = False
    api_url = 'https://api.api-ninjas.com/v1/passwordgenerator?length={}'.format(length, exclude_numbers, exclude_special)
    response = requests.get(api_url, headers={'X-Api-Key': 'dDcouxccX+Ne1OKZj+rRrw==CW8Mg7Tvlk3u8omW'})
    if response.status_code == requests.codes.ok:
        print(response.text)
    else:
        print("Error:", response.status_code, response.text)