# -*- coding: utf-8 -*-
import json, webbrowser
import requests
from colorama import Fore

location = 0


def getLocation():
    global location
    if not location:
        print("Getting Location ... ")
        send_url = 'http://freegeoip.net/json'
        r = requests.get(send_url)
        location = json.loads(r.text)
    return location


def directions(toCity, fromCity = 0):
    if not fromCity:
        fromCity = getLocation()['city']
    url = "https://www.google.com/maps/dir/{0}/{1}".format(fromCity, toCity)
    webbrowser.open(url)


def locateme():
    hcity = getLocation()['city']
    print(Fore.BLUE + "You are at " + hcity + Fore.RESET)


def weather(city = 0):
    if not city:
        city = getLocation()['city']
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
        url = "https://www.google.com/maps/search/{0}+{1}".format(things, city)
    else:
        print(Fore.GREEN + "Hold on!, I'll show " + things + " near you" + Fore.RESET)
        url = "https://www.google.com/maps/search/{0}/@{1},{2}".format(things, getLocation()['latitude'], getLocation()['longitude'])
    webbrowser.open(url)
