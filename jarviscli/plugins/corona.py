import requests
from colorama import Fore
from plugin import plugin, require
from inspect import cleandoc


@require(network=True)
@plugin("corona")
class CoronaInfo:
    """
    corona 					: Display total cases of the world
    corona <Country name | country code>	: Display cases for the specific country"
    corona help					: Print this help


    ** Data provided by: https://api.covid19api.com/
    """

    def __call__(self, jarvis, s):
        if 'help' in s:
            jarvis.say(cleandoc(self.__doc__), Fore.GREEN)
        else:
            corona_info = self.get_corona_info(s)
            if corona_info == "URLError":
                jarvis.say(f"Result was not available at the moment. Try again!!", Fore.RED)
            elif corona_info is None:
                jarvis.say(f"Cant find the country \"{s}\"", Fore.RED)
            else:
                location = corona_info["Country"]
                jarvis.say(f"\t+++++++++++++++++++++++++++++++++++++++", Fore.CYAN)
                jarvis.say(f"\tCorona status: \"{location}\"", Fore.CYAN)
                jarvis.say(f"\t+++++++++++++++++++++++++++++++++++++++", Fore.CYAN)

                new_confirmed = corona_info["NewConfirmed"]
                jarvis.say(f"\tNew confirmed cases	: {new_confirmed}", Fore.YELLOW)

                total_confirmed = corona_info["TotalConfirmed"]
                jarvis.say(f"\tTotal confirmed cases	: {total_confirmed}", Fore.YELLOW)

                new_deaths = corona_info["NewDeaths"]
                jarvis.say(f"\tNew deaths		: {new_deaths}", Fore.RED)

                total_deaths = corona_info["TotalDeaths"]
                jarvis.say(f"\tTotal deaths		: {total_deaths}", Fore.RED)

                new_recovered = corona_info["NewRecovered"]
                jarvis.say(f"\tNew recovered		: {new_recovered}", Fore.GREEN)

                total_recovered = corona_info["TotalRecovered"]
                jarvis.say(f"\tTotal recovered		: {total_recovered}", Fore.GREEN)

    def get_corona_info(self, country_name):
        url = "https://api.covid19api.com/summary"
        response = requests.get(url)
        # Intermittently URL responds with a message - You have reached maximum request limit.
        if response.text == "You have reached maximum request limit.":
            return "URLError"
        result = response.json()
        if country_name:
            for country in result["Countries"]:
                if (
                    country_name == country["Country"].lower()
                    or country_name == country["CountryCode"].lower()
                    or country_name == country["Slug"].lower()
                ):
                    return country
            return None
        global_info = result["Global"]
        global_info["Country"] = "Worldwide"
        return result["Global"]
