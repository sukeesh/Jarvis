# -*- coding: utf-8 -*-
import json, webbrowser

import requests
from colorama import init
from colorama import Fore, Back, Style

def directions(toCity, fromCity = 0):
    if not fromCity:
        send_url = 'http://freegeoip.net/json'
        r = requests.get(send_url)
        j = json.loads(r.text)
        fromCity = j['city']
    url = "https://www.google.co.in/maps/dir/{0}/{1}".format(fromCity, toCity)
    webbrowser.open(url)

def locateme():
    send_url = 'http://freegeoip.net/json'
    r = requests.get(send_url)
    j = json.loads(r.text)
    hcity = j['city']
    print(Fore.BLUE + "You are at " + hcity + Fore.RESET)

def weather(city = 0):
    if not city:
        send_url = 'http://freegeoip.net/json'
        r = requests.get(send_url)
        j = json.loads(r.text)
        city = j['city']
    send_url = (
        "http://api.openweathermap.org/data/2.5/weather?q={0}"
        "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units=metric".format(city)
    )
    r = requests.get(send_url)
    j = json.loads(r.text)
    temperature = j['main']['temp']
    print(Fore.BLUE + "It's " + str(temperature) + " °C in " + str(city) + Fore.RESET)


def searchNear(things, city = 0):
    if city:
        print(Fore.GREEN + "Hold on!, I'll show " + things + " near " + city + Fore.RESET)        
        url = "https://www.google.co.in/maps/search/{0}+{1}".format(things, city)
    else:
        print(Fore.GREEN + "Hold on!, I'll show " + things + " near you" + Fore.RESET)
        send_url = 'http://freegeoip.net/json'
        r = requests.get(send_url)
        j = json.loads(r.text)
        url = "https://www.google.co.in/maps/search/{0}/@{1},{2}".format(things, j['latitude'], j['longitude'])
    webbrowser.open(url)
