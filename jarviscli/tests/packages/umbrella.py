# -*- coding: utf-8 -*-
import json
import requests
from colorama import Fore


def main(city=0):
    send_url = (
        "http://api.openweathermap.org/data/2.5/forecast/daily?q={0}&cnt=1"
        "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units=metric".format(city)
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
