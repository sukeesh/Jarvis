import requests
from plugin import plugin, alias, require
from colorama import Fore


@require(network=True)
@alias("forecast")
@plugin("weather report")
class WeatherReport:
    """The user will input a location as a string, and the WeatherDB database will be
    used to make a GET request and fetch data. Then, the user can see the weather
    forecast for the upcoming week if they wish."""

    def __call__(self, jarvis: "JarvisAPI", s: str) -> None:
        self.print_weather(jarvis)

    def print_weather(self, jarvis: "JarvisAPI"):
        jarvis.say("What city are you located in?")
        jarvis.say("(Only type the city name, not country/province/state.)")
        loc = jarvis.input("Enter city name: ")
        loc = loc.lower()
        x = requests.get('https://weatherdbi.herokuapp.com/data/weather/' + loc)
        y = x.json()
        if 'status' in y and y['status'] == 'fail':
            jarvis.say("Invalid location entered!", color=Fore.RED)
        else:
            jarvis.say("Location: ", Fore.BLUE)
            jarvis.say(y['region'] + ", ")
            jarvis.say("Approx.time: ", Fore.BLUE)
            jarvis.say(y['currentConditions']['dayhour'] + ", ")
            jarvis.say("Temperature: ", Fore.BLUE)
            jarvis.say(str(y['currentConditions']['temp']['c']) + " deg. C, ")
            jarvis.say("Precipitation: ", Fore.BLUE)
            jarvis.say(str(y['currentConditions']['precip']) + ", ")
            jarvis.say("Humidity: ", Fore.BLUE)
            jarvis.say(str(y['currentConditions']['humidity']) + ", ")
            jarvis.say("Wind: ", Fore.BLUE)
            jarvis.say(str(y['currentConditions']['wind']['km']) + " km/h")
            self.ask_for_forecast(jarvis, y)

    def ask_for_forecast(self, jarvis: "JarvisAPI", jason):
        selected_days = jarvis.input(
            "Would you like to see the weather forecast "
            "for the next week? Y/N ")
        selected_days = selected_days.lower()
        if selected_days == 'y':
            for p in jason['next_days']:
                jarvis.say(p['day'] + ": ", Fore.BLUE)
                jarvis.say(p['comment'] + ", with a min. temp. of " + str(p['min_temp']['c']) +
                           " deg. C and a max.temp. of " + str(p['max_temp']['c']) + " deg. C.")
        elif selected_days == 'n':
            jarvis.say("Thank you! Goodbye.")
        else:
            jarvis.say("Invalid input.", color=Fore.RED)
