# -*- coding: utf-8 -*-
import json
import requests
from colorama import Fore


def main(self, s):
    # Trims input s to be just the city/region name
    s = s.replace('time ', '').replace('in ', '')

    # Transforms a city name into coordinates using Google Maps API
    loc = getLocation(s)

    # Gets current date and time using TimeZoneDB API
    send_url = (
        "http://api.timezonedb.com/v2/get-time-zone?"
        "key=BFA6XBCZ8AL5&format=json"
        "&by=position&lat={:.6f}&lng={:.6f}".format(*loc)
    )
    r = requests.get(send_url)
    j = json.loads(r.text)
    time = j['formatted']
    self.dst = j['dst']
    # Prints current date and time as YYYY-MM-DD HH:MM:SS
    print(Fore.MAGENTA + "The current date and time in " +
          str(s).title() + " is: " + str(time) + Fore.RESET)


def getLocation(s):
    send_url = ("http://maps.googleapis.com/maps/api/geocode/json?address={0}&sensor=false".format(s)
                )
    r = requests.get(send_url)
    j = json.loads(r.text)
    lat = j['results'][0]['geometry']['location']['lat']    # Latitude
    lng = j['results'][0]['geometry']['location']['lng']    # Longitude
    # Returns both latitude and longitude as a tupple
    return lat, lng
