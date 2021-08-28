# -*- coding: utf-8 -*-
import json

import requests
from colorama import Fore

from plugin import alias, plugin, require
from utilities.dateTime import WeekDay


@require(network=True, api_key='openweathermap')
@plugin('forecast')
def forecast(jarvis, s, openweathermap=None):
    """
    checks the weather forecast for the next 7 days.
    -- Examples:
        check forecast
        check forecast in Madrid
    """

    cmd_key_words = ['check', 'weather', 'forecast', 'in', 'for', 'a', 'week']
    cmd_words = s.strip().split()
    # location will be defined by the words given that are not the key words
    location = ' '.join(filter(lambda word: word.lower()
                               not in cmd_key_words, cmd_words)).strip()

    # if no location is given, use the current location
    if not location:
        location = "{},{}".format(
            jarvis.get_location(jarvis.LocationFields.CITY),
            jarvis.get_location(jarvis.LocationFields.COUNTRY))

    country = jarvis.get_location(jarvis.LocationFields.COUNTRY)

    # If country is not US, shows weather in Celsius
    units = {
        'url_units': 'metric',
        'str_units': 'ºC'
    }
    # If country is US, shows weather in Fahrenheit
    if country == 'United States':
        units = {
            'url_units': 'imperial',
            'str_units': 'ºF'
        }

    send_url = (
        "http://api.openweathermap.org/data/2.5/forecast/daily?q={0}&cnt={1}"
        "&APPID={2}&units={3}".format(
            location, '7', openweathermap, units['url_units'])
    )

    r = requests.get(send_url)
    j = json.loads(r.text)

    week_from_today = WeekDay().get_week_from_today()

    try:
        jarvis.say(
            "Weather forecast in {} for the next 7 days.".format(
                j['city']['name'].title()
            ),
            Fore.BLUE
        )

        for cnt, day_dict in enumerate(j['list']):
            jarvis.say("{}:".format(week_from_today[cnt]), Fore.BLUE)
            jarvis.say("\tWeather: {}".format(
                day_dict['weather'][0]['main']), Fore.BLUE)
            jarvis.say(
                "\tMax temperature: {} {}".format(
                    round(day_dict['temp']['max'], 1), units['str_units']),
                Fore.BLUE
            )
            jarvis.say(
                "\tMin temperature: {} {}\n".format(

                    round(day_dict['temp']['min'], 1), units['str_units']),
                Fore.BLUE
            )
    except KeyError:
        jarvis.say("The forecast information could not be found.", Fore.RED)


@require(network=True, api_key='openwathermap')
@plugin("umbrella")
def do_umbrella(self, s, openwathermap=None):
    """If you're leaving your place, Jarvis will inform you if you might need an umbrella or not."""
    city = "{},{}".format(
        jarvis.get_location(jarvis.LocationFields.CITY),
        jarvis.get_location(jarvis.LocationFields.COUNTRY))

    send_url = (
        "http://api.openweathermap.org/data/2.5/forecast/daily?q={0}&cnt=1&APPID={1}&units=metric".format(
            city, openweathermap)
    )

    r = requests.get(send_url)
    j = json.loads(r.text)
    rain = j['list'][0]['weather'][0]['id']
    if rain >= 300 and rain <= 500:  # In case of drizzle or light rain
        print(
            Fore.CYAN
            + "It appears that you might need an umbrella today."
            + Fore.RESET)
    elif rain > 700:
        print(
            Fore.CYAN
            + "Good news! You can leave your umbrella at home for today!"
            + Fore.RESET)
    else:
        print(
            Fore.CYAN
            + "Uhh, bad luck! If you go outside, take your umbrella with you."
            + Fore.RESET)
