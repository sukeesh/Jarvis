# -*- coding: utf-8 -*-
import json
import requests
from . import mapps
from packages import weather_pinpoint as pinpoint
from packages.memory.memory import Memory
from colorama import Fore


def main(self, s):
    # Trim input command to get only the location
    loc = s.replace(
        'weather',
        '').replace(
        'in ',
        '').replace(
            'at ',
        '').strip()

    # Checks country
    country = mapps.get_location()['country_name']

    # If country is US, shows weather in Fahrenheit
    if country == 'United States':
        send_url = (
            "http://api.openweathermap.org/data/2.5/weather?q={0}"
            "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units=imperial".format(
                loc)
        )
        unit = ' ºF in '

    # If country is not US, shows weather in Celsius
    else:
        send_url = (
            "http://api.openweathermap.org/data/2.5/weather?q={0}"
            "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units=metric".format(loc)
        )
        unit = ' ºC in '
    r = requests.get(send_url)
    j = json.loads(r.text)

    if 'message' in list(
            j.keys()) and (
            'city not found' in j['message'] or 'Nothing to geocode' in j['message']):
        print("Location invalid. Please be more specific")
        return pinpoint.main(Memory(), self, s)

    temperature = j['main']['temp']
    description = j['weather'][0]['main']
    location = j['name']
    print("{COLOR}It's {TEMP}{UNIT}{LOCATION} ({DESCRIPTION}){COLOR_RESET}"
          .format(COLOR=Fore.BLUE, COLOR_RESET=Fore.RESET,
                  TEMP=temperature, UNIT=unit, LOCATION=location.title(),
                  DESCRIPTION=description))
