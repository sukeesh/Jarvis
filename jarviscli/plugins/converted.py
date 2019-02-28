"""
Plugins not fully converted but simply "wrapped" as plugins.
"""
from packages import (directions_to, forecast, mapps, near_me,
                      timeIn, weather_pinpoint, weatherIn)
from packages.systemOptions import update_system


from plugin import plugin, complete, require


@require(network=True)
@plugin("check time")
def check_time(self, s):
    """
    checks the current time in any part of the globe.
    -- Examples:
        check time in Manchester (UK)
    """
    timeIn.main(self._jarvis, s)


@plugin("check forecast")
def check_forecast(self, s):
    """
    checks the weather forecast for the next 7 days.
    -- Examples:
        check forecast
        check forecast in Madrid
    """
    forecast.main(self, s)


@plugin("check weather")
def check_weather(self, s):
    """
    weather in *: checks the current weather in any part of the globe.
    -- Examples:
        check weather in Canada
    """
    weatherIn.main(self._jarvis, s)


@plugin("directions")
def directions(self, data):
    """
    Get directions about a destination you are interested to.
    -- Example:
        directions to the Eiffel Tower
    """
    self = self._jarvis

    try:
        directions_to.main(data)
    except ValueError:
        print("Please enter destination")
    except ConnectionError:
        print(CONNECTION_ERROR_MSG)


@plugin("near")
def do_near(self, data):
    """
    Jarvis can find what is near you!
    -- Examples:
        restaurants near me
        museums near the eiffel tower
    """
    near_me.main(data)


@plugin("pinpoint")
def do_pinpoint(self, s):
    """Jarvis will pinpoint your location."""
    try:
        mapps.locate_me()
    except ConnectionError:
        print(CONNECTION_ERROR_MSG)


@plugin("umbrella")
def do_umbrella(self, s):
    """If you're leaving your place, Jarvis will inform you if you might need an umbrella or not."""
    self = self._jarvis

    s = 'umbrella'
    try:
        weather_pinpoint.main(self.memory, self, s)
    except ConnectionError:
        print(CONNECTION_ERROR_MSG)


@complete("location", "system")
@plugin("update")
def do_update(self, s):
    """
    location: Updates location.
    system: Updates system.
    """
    self = self_jarvis

    if "location" in s:
        location = self.memory.get_data('city')
        loc_str = str(location)
        print_say("Your current location is set to " + loc_str, self)
        print_say("What is your new location?", self)
        i = input()
        self.memory.update_data('city', i)
        self.memory.save()
    elif "system" in s:
        update_system()


@plugin("weather")
def do_weather(self, s):
    """Get information about today's weather in your current location."""
    self = self._jarvis

    try:
        word = s.strip()
        if(len(word) > 1):
            weatherIn.main(self, s)
        else:
            weather_pinpoint.main(self.memory, self, s)
    except ConnectionError:
        print(CONNECTION_ERROR_MSG)
