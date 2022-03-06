import requests
from plugin import plugin, alias, require


class weatherReportException(Exception):
    """An exception for invalid location inputs"""


@require(network=True)
@alias("forecast")
@plugin("weather report")
class WeatherReport:
    """The user will input a location as a string, and the WeatherDB database will be used to make a GET request and
    fetch data. Then, the user can pick future days from the upcoming week to see the weather report for. """

    def __call__(self, jarvis: "JarvisAPI", s: str) -> None:
        print_weather()


def print_weather():
    loc = 'kamloops'
    x = requests.get('https://weatherdbi.herokuapp.com/data/weather/' + loc, )
    y = x.json()
    print("Location: " + y['region'] + ", ")
    print("Approx. time: " + y['currentConditions']['dayhour'] + ", ")
    print("Temperature: " + str(y['currentConditions']['temp']['c']) + " deg. C, ")
    print("Precipitation: " + str(y['currentConditions']['precip']) + ", ")
    print("Humidity: " + str(y['currentConditions']['humidity']) + ", ")
    print("Wind :" + str(y['currentConditions']['wind']['km']) + " km/h")


if __name__ == '__weather_report__':
    print_weather()
