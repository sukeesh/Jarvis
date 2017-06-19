# -*- coding: utf-8 -*-
from utilities.GeneralUtilities import print_say
from colorama import Fore
import json
import mapps
import requests

def main(self, s):
    cmd_key_words = ['check', 'weather', 'forecast', 'in', 'for']
    cmd_words = s.strip().split()
    # location will be defined by the words given that are not the key words
    location = ' '.join(filter(lambda word: word.lower() not in cmd_key_words, cmd_words)).strip()

    # if no location is given, use the current location
    if not location:
        print_say("Weather forecast in the current location for the next 7 days.", self, Fore.BLUE)
        # if no 'location' provided, store the current location in 'location'
        location = 'Madrid'

    # otherwise use the location given
    print_say("Weather forecast in {} for the next 7 days.".format(location.title()), self, Fore.BLUE)
 

    country = mapps.getLocation()['country_name']

    # If country is not US, shows weather in Celsius
    units = {
        'url_units': 'metric',
        'str_units': ' ºC in '
    }
    # If country is US, shows weather in Fahrenheit
    if country == 'United States':
        units = {
            'url_units': 'imperial',
            'str_units': ' ºF in '
        }

    send_url = (
        "http://api.openweathermap.org/data/2.5/forecast/daily?q={0}&cnt={1}"
        "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units={2}".format(location, '7', units['url_units'])
    )

    r = requests.get(send_url)
    j = json.loads(r.text)
