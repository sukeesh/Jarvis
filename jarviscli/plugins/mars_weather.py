import requests
from colorama import Fore
from plugin import plugin, require
import datetime

API_KEY = 'OsZ9DfFtdgR6zPlVjxFTch1Np5zAcqt9g9i34ga2'
headers = {'X-Auth-Token': API_KEY}
url = 'https://api.nasa.gov/insight_weather/?api_key=OsZ9DfFtdgR6zPlVjxFTch1Np5zAcqt9g9i34ga2&feedtype=json&ver=1.0'


@require(network=True)
@plugin('mars weather')
def mars_weather(jarvis, s):
    print("")
    jarvis.say("~> I'll show you MARS weather forecast", Fore.RED)
    print("")

    r = fetch()
    x = r['sol_keys']

    count = 0

    for i in x:
        dt = str(datetime.date.today() + datetime.timedelta(days=count))
        jarvis.say(dt, Fore.BLUE)

        season = "SEASON: " + r[i]['Season']
        jarvis.say(season, Fore.BLUE)
        print("")

        get_temperature(jarvis, r, i)
        print("")

        get_wind(jarvis, r, i)
        print("")

        get_pressure(jarvis, r, i)
        print("")

        count += 1


def fetch():
    r = requests.get(url, headers=headers)
    r = r.json()
    if "errorCode" in r.keys():
        return None
    return r


def get_temperature(jarvis, fulldata, sol):
    jarvis.say("TEMPERATURE:", Fore.RED)
    temperature = fulldata[sol]['AT']

    avg = "AVG temp: " + str(round(temperature['av'], 1)) + " ºF"
    ct = "Recorded samples: " + str(temperature['ct'])
    min_temp = "MIN temp: " + str(round(temperature['mn'], 1)) + " ºF"
    max_temp = "MAX temp: " + str(round(temperature['mx'], 1)) + " ºF"

    jarvis.say(avg, Fore.RED)
    jarvis.say(min_temp, Fore.RED)
    jarvis.say(max_temp, Fore.RED)
    jarvis.say(ct, Fore.RED)


def get_wind(jarvis, fulldata, sol):
    jarvis.say("WIND:", Fore.GREEN)
    wind = fulldata[sol]['HWS']

    avg = "AVG speed: " + str(round(wind['av'], 1)) + " mph"
    ct = "Recorded samples: " + str(wind['ct'])
    min_speed = "MIN speed: " + str(round(wind['mn'], 1)) + " mph"
    max_speed = "MAX speed: " + str(round(wind['mx'], 1)) + " mph"

    jarvis.say(avg, Fore.GREEN)
    jarvis.say(min_speed, Fore.GREEN)
    jarvis.say(max_speed, Fore.GREEN)
    jarvis.say(ct, Fore.GREEN)


def get_pressure(jarvis, fulldata, sol):
    jarvis.say("PRESSURE:", Fore.YELLOW)
    pressure = fulldata[sol]['PRE']

    avg = "AVG pressure: " + str(round(pressure['av'], 1)) + " Pa"
    ct = "Recorded samples: " + str(pressure['ct'])
    min_pressure = "MIN pressure: " + str(round(pressure['mn'], 1)) + " Pa"
    max_pressure = "MAX pressure: " + str(round(pressure['mx'], 1)) + " Pa"

    jarvis.say(avg, Fore.YELLOW)
    jarvis.say(min_pressure, Fore.YELLOW)
    jarvis.say(max_pressure, Fore.YELLOW)
    jarvis.say(ct, Fore.YELLOW)
