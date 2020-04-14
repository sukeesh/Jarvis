import requests
from colorama import Fore
from plugin import plugin, require


@require(network=True)
@plugin("corona")
class CoronaInfo:
    def __call__(self, jarvis, s):
        corona_info = self.get_corona_info(s)
        if corona_info:
            location = corona_info["CountryCode"]
            jarvis.say(f"\"{location}\" corona status:", Fore.CYAN)

            new_confirmed = corona_info["NewConfirmed"]
            jarvis.say(f"\tnew confirmed cases: {new_confirmed}", Fore.YELLOW)

            total_confirmed = corona_info["TotalConfirmed"]
            jarvis.say(f"\ttotal confirmed cases: {total_confirmed}", Fore.YELLOW)

            new_deaths = corona_info["NewDeaths"]
            jarvis.say(f"\tnew deaths: {new_deaths}", Fore.RED)

            total_deaths = corona_info["TotalDeaths"]
            jarvis.say(f"\ttotal deaths: {total_deaths}", Fore.RED)

            new_recovered = corona_info["NewRecovered"]
            jarvis.say(f"\tnew recovered: {new_recovered}", Fore.GREEN)

            total_recovered = corona_info["TotalRecovered"]
            jarvis.say(f"\total recovered: {total_recovered}", Fore.GREEN)
        else:
            jarvis.say(f"Cant find the country \"{s}\"", Fore.RED)

    def get_corona_info(self, country_name):
        url = "https://api.covid19api.com/summary"
        response = requests.get(url)
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
        global_info["CountryCode"] = "Worldwide"
        return result["Global"]
