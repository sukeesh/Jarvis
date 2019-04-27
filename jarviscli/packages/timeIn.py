# -*- coding: utf-8 -*-
import os
import shutil
import json
import requests
from colorama import Fore

# this sets the path to the modules directory not the directory it was
# call from
module_path = os.path.dirname(__file__)
module_path = module_path + '/../data/'


def main(self, s):
    # Trims input s to be just the city/region name
    s = s.replace('time ', '').replace('in ', '')

    exists = os.path.isfile(module_path + 'key_timein.json')
    if not exists:
        shutil.copy2(
            module_path
            + 'samplekey_timein.json',
            module_path
            + 'key_timein.json')
        print(
            Fore.RED
            + "Generate api key here: https://developers.google.com/maps/documentation/geocoding/start?hl=en_US")
        print(
            Fore.RED
            + "and add it to jarviscli/data/key_timein.json"
            + Fore.RESET)
        return

    # Transforms a city name into coordinates using Google Maps API
    loc = getLocation(s)
    if loc is None:
        return
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
    print("{COLOR}The current date and time in {LOC} is: {TIME}{COLOR_RESET}"
          .format(COLOR=Fore.MAGENTA, COLOR_RESET=Fore.RESET,
                  LOC=str(s).title(), TIME=str(time)))


def getLocation(s):
    file_path = module_path + 'key_timein.json'
    with open(file_path) as json_file:
        data = json.load(json_file)
    if 'timein' not in data or data['timein'] == 'insertyourkeyhere':
        print(Fore.RED + "API key not added")
        print(
            Fore.RED
            + "Generate api key here: https://developers.google.com/maps/documentation/geocoding/start?hl=en_US")
        print(
            Fore.RED
            + "and add it to jarviscli/data/key_timein.json"
            + Fore.RESET)
        return None
    key = data['timein']
    send_url = (
        "https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}".format(s, key))
    # https://developers.google.com/maps/documentation/geocoding/start?hl=en_US
    # https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=YOUR_API_KEY
    r = requests.get(send_url)
    j = json.loads(r.text)
    try:
        lat = j['results'][0]['geometry']['location']['lat']    # Latitude
        lng = j['results'][0]['geometry']['location']['lng']    # Longitude
        # Returns both latitude and longitude as a tuple
        return lat, lng
    except IndexError:
        # Error handled after try except
        pass
    raise Exception(r.text)
