import json

import requests
from plugin import plugin, alias, require
from colorama import Fore

#import requests

# lat, lon = 38.8951, -77.0364
# url = f"https://api.weather.gov/points/{lat},{lon}"

#https://api.weather.gov
#https://api.weather.gov/points/{latitude},{longitude}

@require(network=True)
@alias("forecast")
@plugin("weather report")
def run_weather_plugin(jarvis, s):
    weather = WeatherReport(jarvis)
    weather.enterLoc()

class WeatherReport:
    def __init__(self, jarvis=None):
        self.jarvis = jarvis

    def say(self, msg):
        if self.jarvis:
            self.jarvis.say(msg)
        else:
            print(msg)

    def geocode_nominatim(self, location):
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "JarvisWeather/1.0 (https://github.com/sukeesh/Jarvis)"
        }

        try:
            res = requests.get(url, params=params, headers=headers, timeout=5)
            res.raise_for_status()
            data = res.json()

            if not data:
                self.say(f"❌ Could not find location: {location}")
                return None, None

            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        except Exception as e:
            self.say(f"⚠️ Geocoding error: {e}")
            return None, None

    def get_forecast_url(self, lat, lon):
        url = f"https://api.weather.gov/points/{lat},{lon}"
        headers = {
            "User-Agent": "JarvisWeather/1.0 (https://github.com/sukeesh/Jarvis)",
            "Accept": "application/geo+json"
        }

        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            data = res.json()

            if "properties" not in data or "forecast" not in data["properties"]:
                self.say("❌ Unexpected API response format from weather.gov:")
                import json
                self.say(json.dumps(data, indent=2))  # Debug print
                return None

            return data["properties"]["forecast"]

        except requests.exceptions.RequestException as e:
            self.say(f"⚠️ Network error: {e}")
            return None
        except Exception as e:
            self.say(f"⚠️ Unexpected error: {e}")
            return None

    def fetch_forecast(self, forecast_url):
        headers = {
            "User-Agent": "JarvisWeather/1.0 (https://github.com/sukeesh/Jarvis)",
            "Accept": "application/geo+json"
        }
        res = requests.get(forecast_url, headers=headers)
        data = res.json()
        self.say("fetching data...")
        # self.say(json.dumps(data, indent=2))
        periods = data["properties"]["periods"]
        self.say("getting forecast...")
        self.display_forecast(periods)
        return data["properties"]["periods"]

    def display_forecast(self, periods):
        self.say("\n📆 Forecast:\n" + "-" * 30)
        for p in periods[:5]:  # Show next 5 periods
            self.say(f"{p['name']}: {p['temperature']}°F, {p['shortForecast']}")
            self.say(f"↪️ {p['detailedForecast']}\n")

    def enterLoc(self):
        location = input("📍 Enter a U.S. city and state: ").strip()
        lat, lon = self.geocode_nominatim(location)

        if lat is None or lon is None:
            return

        forecast_url = self.get_forecast_url(lat, lon)
        if not forecast_url:
            return

        periods = self.fetch_forecast(forecast_url)
        if not periods:
            self.say("❌ Could not fetch forecast data.")
            return

    # def __call__(self, jarvis: "JarvisAPI", s: str) -> None:
    #     self.print_weather(jarvis)
    #
    # def print_weather(self, jarvis: "JarvisAPI"):
    #     jarvis.say("Are you located in the United States?")
    #     jarvis.say("What city are you located in?")
    #     jarvis.say("(Only type the city name, not country/province/state.)")
    #     loc = jarvis.input("Enter city name: ")
    #     loc = loc.lower()
    #     jarvis.say("What state are you located in?")
    #     jarvis.say("(Only type the state name, not country)")
    #
    #     x = requests.get('https://api.weather.gov' + loc)
    #     y = x.json()
    #     if 'status' in y and y['status'] == 'fail':
    #         jarvis.say("Invalid location entered!", color=Fore.RED)
    #     else:
    #         jarvis.say("Location: ", Fore.BLUE)
    #         jarvis.say(y['region'] + ", ")
    #         jarvis.say("Approx.time: ", Fore.BLUE)
    #         jarvis.say(y['currentConditions']['dayhour'] + ", ")
    #         jarvis.say("Temperature: ", Fore.BLUE)
    #         jarvis.say(str(y['currentConditions']['temp']['c']) + " deg. C, ")
    #         jarvis.say("Precipitation: ", Fore.BLUE)
    #         jarvis.say(str(y['currentConditions']['precip']) + ", ")
    #         jarvis.say("Humidity: ", Fore.BLUE)
    #         jarvis.say(str(y['currentConditions']['humidity']) + ", ")
    #         jarvis.say("Wind: ", Fore.BLUE)
    #         jarvis.say(str(y['currentConditions']['wind']['km']) + " km/h")
    #         self.ask_for_forecast(jarvis, y)
    #
    # def ask_for_forecast(self, jarvis: "JarvisAPI", jason):
    #     selected_days = jarvis.input(
    #         "Would you like to see the weather forecast "
    #         "for the next week? Y/N ")
    #     selected_days = selected_days.lower()
    #     if selected_days == 'y':
    #         for p in jason['next_days']:
    #             jarvis.say(p['day'] + ": ", Fore.BLUE)
    #             jarvis.say(p['comment'] + ", with a min. temp. of " + str(p['min_temp']['c']) +
    #                        " deg. C and a max.temp. of " + str(p['max_temp']['c']) + " deg. C.")
    #     elif selected_days == 'n':
    #         jarvis.say("Thank you! Goodbye.")
    #     else:
    #         jarvis.say("Invalid input.", color=Fore.RED)
