# -*- coding: utf-8 -*-
import json
import requests
from colorama import Fore


def main(self, s):
    loc = s.replace('weather ', '').replace('in ', '')  # Trim input command to get only the location
    send_url = (
        "http://api.openweathermap.org/data/2.5/weather?q={0}"
        "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units=metric".format(loc)
    )
    r = requests.get(send_url)
    j = json.loads(r.text)
    temperature = j['main']['temp']
    description = j['weather'][0]['main']
    print(Fore.BLUE + "It's " + str(temperature) + " °C in " + str(loc.title()) + " (" + str(description) + ")" + Fore.RESET)