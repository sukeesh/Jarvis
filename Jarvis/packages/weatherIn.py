# -*- coding: utf-8 -*-
import json
import requests
import mapps
import packages.weather_pinpoint as pinpoint
from packages.memory.memory import Memory
from colorama import Fore


def main(self, s, forecast=False):
    # Trim input command to get only the location
    loc = s.replace('weather', '').replace('in ', '').strip()

    # Checks country to determine which units to output
    country = mapps.getLocation()['country_name']
    if country == 'United States':
        units = 'imperial'
        unit  = ' ºF '
    else:
        units = 'metric'
        unit  = ' ºC '

    # request a forecast or the current weather?
    if forecast == False:
        get_weather(loc, units, unit)
    else:
        get_forecast(loc, units, unit)



def get_weather(loc, units, unit):
    # create URL
    send_url = (
            "http://api.openweathermap.org/data/2.5/weather?q={0}"
            "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units={1}".format(loc, units)
        )

    # send request and parse into JSON
    r = requests.get(send_url)
    j = json.loads(r.text)

    # error checking
    if ('message' in j.keys() and ('city not found' in str(j['message']) or
        'Nothing to geocode' in str(j['message'])) ):
        return pinpoint.main(Memory(), self, s)

    # pull data from JSON and print
    temperature = j['main']['temp']
    description = j['weather'][0]['main']
    location = j['name']
    print(Fore.BLUE + "It's " + str(temperature) + unit + "in " + str(location.title()) +
          " (" + str(description) + ")" + Fore.RESET)


def get_forecast(loc, units, unit):
    # create URL
    send_url = (
            "http://api.openweathermap.org/data/2.5/forecast/daily?q={0}"
            "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units={1}&cnt=7".format(loc, units)
        )

    # send request and parse into JSON
    r = requests.get(send_url)
    j = json.loads(r.text)

    # error checking
    if ('message' in j.keys() and ('city not found' in str(j['message']) or
        'Nothing to geocode' in str(j['message'])) ):
        return pinpoint.main(Memory(), self, s)

    # pull data from JSON and print
    print(Fore.BLUE + "Seven-Day Forecast for {0}:".format(loc))
    for i in range(7):
        min_temp = j['list'][i]['temp']['min']
        max_temp = j['list'][i]['temp']['max']
        weather  = j['list'][i]['weather'][0]['main']
        print("\tDay {0}:  Min Temp = {1}".format(i+1, min_temp) + unit +
              "\tMax Temp = {0}".format(max_temp) + unit +
              "\t({0})".format(weather))

