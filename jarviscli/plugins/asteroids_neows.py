import requests
from colorama import Fore
from plugin import plugin, require
import datetime

API_KEY = '1ebd3b92bf5041249f8c1e7a540ce98c'
headers = {'X-Auth-Token': API_KEY}
# url = 'https://api.nasa.gov/neo/rest/v1/feed?start_date=2020-07-10&end_date=2020-07-10&api_key=DqXuTRFieGmR5EbdTpPA0tIbDybBhuVmWNerhOdN'


@require(network=True)
@plugin('neows')
def neows(jarvis, s):
    option = get_option(jarvis)
    if option == 8:
        return

    dt = str(datetime.date.today() + datetime.timedelta(days=option - 1))
    print_objects(jarvis, dt)


def print_objects(jarvis, dt):
    url = 'https://api.nasa.gov/neo/rest/v1/feed?start_date=' + dt
    url += '&end_date=' + dt
    url += '&api_key=DqXuTRFieGmR5EbdTpPA0tIbDybBhuVmWNerhOdN'

    r = fetch(url)
    day = r["near_earth_objects"]
    neos = day[dt]
    jarvis.say("Near earth objects: " + str(r["element_count"]), Fore.RED)
    print()

    for i in range(0, r["element_count"]):
        print("---" + str(i + 1) + "---")
        name = "Name: " + neos[i]["name"]
        jarvis.say(name, Fore.BLUE)

        jpl = "Nasa jpl url: " + neos[i]["nasa_jpl_url"]
        jarvis.say(jpl, Fore.BLUE)

        hazardous = "Is potentially hazardous asteroid: "
        if neos[i]["is_potentially_hazardous_asteroid"]:
            hazardous += "YES"
        else:
            hazardous += "NO"
        jarvis.say(hazardous, Fore.BLUE)

        sentry = "Is sentry object: "
        if neos[i]["is_sentry_object"]:
            sentry += "YES"
        else:
            sentry += "NO"
        jarvis.say(sentry, Fore.BLUE)

        print()


def get_option(jarvis):
    jarvis.say("~> I can detect near earth objects at given date", Fore.RED)
    jarvis.say("~> Which date do you want?", Fore.RED)

    day1 = datetime.date.today()
    day2 = datetime.date.today() + datetime.timedelta(days=1)
    day3 = datetime.date.today() + datetime.timedelta(days=2)
    day4 = datetime.date.today() + datetime.timedelta(days=3)
    day5 = datetime.date.today() + datetime.timedelta(days=4)
    day6 = datetime.date.today() + datetime.timedelta(days=5)
    day7 = datetime.date.today() + datetime.timedelta(days=6)

    print("1: " + str(day1))
    print("2: " + str(day2))
    print("3: " + str(day3))
    print("4: " + str(day4))
    print("5: " + str(day5))
    print("6: " + str(day6))
    print("7: " + str(day7))
    print("8: Exit")
    print()

    while True:
        try:
            option = int(jarvis.input("Enter your choice: ", Fore.GREEN))
            if option >= 1 and option <= 8:
                return option
            else:
                jarvis.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
        except ValueError:
            jarvis.say(
                "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
        print()


def fetch(url):
    r = requests.get(url, headers=headers)
    r = r.json()
    if "errorCode" in r.keys():
        return None
    return r
