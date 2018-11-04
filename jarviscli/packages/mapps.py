# -*- coding: utf-8 -*-
import json
import webbrowser
import requests
from colorama import Fore

location = 0


def get_location():
    global location
    if not location:
        print("Getting Location ... ")
        send_url = 'http://api.ipstack.com/check?access_key=8f7b2ef26a8f5e88eb25ae02606284c2&output=json&legacy=1'
        r = requests.get(send_url)
        location = json.loads(r.text)
    return location


def directions(to_city, from_city=0):
    if not from_city:
        from_city = get_location()['city']
    url = "https://www.google.com/maps/dir/{0}/{1}".format(from_city, to_city)
    webbrowser.open(url)


def locate_me():
    hcity = get_location()['city']
    print(Fore.BLUE + "You are at " + hcity + Fore.RESET)


def weather(city=None):
    if not city:
        city = get_location()['city']

    # Checks country
    country = get_location()['country_name']

    # If country is US, shows weather in Fahrenheit
    if country == 'United States':
        send_url = (
            "http://api.openweathermap.org/data/2.5/weather?q={0}"
            "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units=imperial".format(
                city)
        )
        unit = ' ºF in '

    # If country is not US, shows weather in Celsius
    else:
        send_url = (
            "http://api.openweathermap.org/data/2.5/weather?q={0}"
            "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units=metric".format(
                city)
        )
        unit = ' ºC in '
    r = requests.get(send_url)
    j = json.loads(r.text)

    # check if the city entered is not found
    if 'message' in j and j['message'] == 'city not found':
        print(Fore.BLUE + "City Not Found" + Fore.RESET)
        return False

    else:
        temperature = j['main']['temp']
        description = j['weather'][0]['main']
        print("{COLOR}It's {TEMP}{UNIT}{CITY} ({DESCR}){COLOR_RESET}"
              .format(COLOR=Fore.BLUE, COLOR_RESET=Fore.RESET,
                      TEMP=temperature, UNIT=unit, CITY=city,
                      DESCR=description))

    return True


def search_near(things, city=0):
    if city:
        print("{COLOR}Hold on! I'll show {THINGS} near {CITY}{COLOR_RESET}"
              .format(COLOR=Fore.GREEN, COLOR_RESET=Fore.RESET,
                      THINGS=things, CITY=city))
    else:
        print("{COLOR}Hold on!, I'll show {THINGS} near you{COLOR_RESET}"
              .format(COLOR=Fore.GREEN, COLOR_RESET=Fore.RESET, THINGS=things))
        url = "https://www.google.com/maps/search/{0}/@{1},{2}".format(
            things, get_location()['latitude'], get_location()['longitude'])
    webbrowser.open(url)
