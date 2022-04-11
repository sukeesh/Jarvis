#Import necessary packages
import requests
from plugin import plugin, alias, require
from colorama import Fore
import datetime

@require(network=True)
@alias("forecast")
@plugin("weather report")

class WeatherReport:
    """Get the weather forecast for the current day and next 7 days. The user can input a location and
        recieve weather data from OpenWeatherMap API."""

    # Fetch information using API key
    def __call__(self, jarvis, s: str) -> None:
        self.apikey = "c15e25198031e54d78ef4740a7b53e5f"
        lat, lon = self.get_location(jarvis, s)
        unit = self.get_unit(jarvis)
        self.print_forecast(jarvis, lat, lon, unit)

    # Convert unix time to readable text with adjusted timezone
    def convertTime(self, time, shift):
        return datetime.datetime.utcfromtimestamp(int(time) + int(shift)).replace(tzinfo=datetime.timezone.utc).strftime("%A, %B %-d, %Y")
    
    # Prompt user to input location
    def get_location(self, jarvis, s):
        while True:
            if not s:
                jarvis.say("Which city do you want to get the weather forecast for?", color = Fore.GREEN)
                res = jarvis.input("Enter the city's name: ", color = Fore.GREEN)
            else:
                res = s
            res = res.lower()
            if res == "":
                continue
            x = requests.get(f"https://api.openweathermap.org/geo/1.0/direct?q={res}&limit=5&appid={self.apikey}")
            y = x.json()
            if (len(y) == 0):
                jarvis.say("No cities found. Please try again.\n", color = Fore.RED)
            else:
                break
        while True:
            for i, location in enumerate(y):
                jarvis.say(f"{str(i+1)}. {location['name']}, {location['state'] + ', ' if 'state' in location  else ''}{location['country']}", color = Fore.YELLOW)
            loc = jarvis.input("Enter the number of the correct location: ", color = Fore.GREEN)
            if loc.isnumeric() and int(loc) > 0 and int(loc) <= len(y):
                break
            else:
                jarvis.say("Invalid input. Please try again.\n", color = Fore.RED)
        return y[int(loc)-1]['lat'], y[int(loc)-1]['lon']

    #Prompt user to input measurement unit
    def get_unit(self, jarvis):
        while True:
            unit = jarvis.input("Which measurement unit do you want to use: imperial or metric? ", color = Fore.GREEN).lower()
            if unit == "imperial" or unit == "metric": 
                break
            else:
                jarvis.say("Invalid input. Please try again.\n", color = Fore.RED)
        return unit

    # Convert wind degree to direction
    def get_wind_direction(self, degrees):
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        val = int((degrees/22.5) + .5)
        return directions[val % 16]

    # Define forecast output
    def print_forecast(self, jarvis, lat, lon, unit):
        deg = "°F" if unit == "imperial" else "°C"
        wind = "mph" if unit == "imperial" else "km/h"
        x = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&units=metric&exclude=current,minutely,hourly,alerts&appid={self.apikey}")
        y = x.json()
        jarvis.say("")
        for day in y['daily']:
            jarvis.say(Fore.YELLOW + "Local Date: " + Fore.WHITE + self.convertTime(day['dt'], y['timezone_offset']))
            jarvis.say(Fore.BLUE + "Condition: " + Fore.WHITE + day['weather'][0]["main"] + " (" + day['weather'][0]["description"] + ")")
            jarvis.say(Fore.BLUE + "Temperatures: ")
            jarvis.say(Fore.BLUE + "    Min/Max Temperature: " + Fore.WHITE + str(day['temp']['min']) + f"{deg} / " + str(day['temp']['max']) + f"{deg}")
            jarvis.say(Fore.BLUE + "    Day: "  + Fore.WHITE + str(day['temp']['day']) + f"{deg}" + " (feels like: " + str(day['feels_like']['day']) + f"{deg})")
            jarvis.say(Fore.BLUE + "    Night: "  + Fore.WHITE + str(day['temp']['night']) + f"{deg}" + " (feels like: " + str(day['feels_like']['night']) + f"{deg})")
            jarvis.say(Fore.BLUE + "Humidity: " + Fore.WHITE + str(day['humidity']) + "%")
            jarvis.say(Fore.BLUE + "Precipitation: " + Fore.WHITE + "{:.0%}".format(day['pop']))
            if ('rain' in day):
                jarvis.say(Fore.BLUE + "Rain volume: " + Fore.WHITE + str(day['rain']) + "mm")
            if ('snow' in day):
                jarvis.say(Fore.BLUE + "Snow volume: " + Fore.WHITE + str(day['snow']) + "mm")
            jarvis.say(Fore.BLUE + "Humidity: " + Fore.WHITE + str(day['humidity']) + "%")
            jarvis.say(Fore.BLUE + "Wind: " + Fore.WHITE + str(day['wind_speed']) + f" {wind} " + self.get_wind_direction(day['wind_deg']))
            jarvis.say("")
