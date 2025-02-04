from plugin import plugin, require
import requests


@require(network=True)
@plugin("countryinfo")
class country_info:
    """
    Welcome to the Countryinfo plugin documentation! Here you will be able
    to find all the functionalities of the plugin.
    Usage: Type countryinfo and follow the instructions.
    This plugin gives you several important details corresponding to country
    which is asked as an input
    Please enter country name in smallcase
    Go on and explore your information!!
    """

    def __call__(self, jarvis, s):
        jarvis.say("Welcome!")
        print()
        country_fetch = self.get_country(jarvis)
        if country_fetch is not None:
            self.country_info(jarvis, country_fetch)

    def get_country(self, jarvis):
        """
        function creates request to api and fetches the corresponding data
        """
        while True:
            country = jarvis.input(
                "Enter the name of the country or type exit to leave: "
            )
            if country == "":
                jarvis.say("Please enter valid input.")
            elif country == "exit":
                return
            else:
                url = "https://restcountries.com/v3.1/name/" + country
                r = requests.get(url)
                if isinstance(r.json(), dict):
                    jarvis.say("Country not found.")
                else:
                    return r.json()

    def country_info(self, jarvis, country_fetch):
        capital = country_fetch[0]["capital"][0]
        population = country_fetch[0]["population"]
        region = country_fetch[0]["region"]
        currency = list(country_fetch[0]["currencies"].values())[0]["name"]
        currency_symbol = list(country_fetch[0]["currencies"].values())[0]["symbol"]
        time_zone = country_fetch[0]["timezones"][0]
        iso_code = country_fetch[0]["cca2"]
        income = self.get_income(jarvis, iso_code)[1][0]["incomeLevel"]["value"]

        print()
        jarvis.say("Capital: " + str(capital))
        jarvis.say("Currency: " + str(currency))
        jarvis.say("Currency Symbol: " + str(currency_symbol))
        jarvis.say("Population: " + str(population))
        jarvis.say("Region: " + str(region))
        jarvis.say("Time Zone: " + str(time_zone))
        jarvis.say("Country Code: " + str(iso_code))
        jarvis.say("Income Level: " + str(income))

        return

    def get_income(self, jarvis, iso_code):
        """
        this is a fetch function to get income level of one country, given their ISO code
        """
        while True:
            url = "http://api.worldbank.org/v2/country/%s?format=json" % iso_code
            r = requests.get(url)
            if isinstance(r.json(), dict):
                jarvis.say("Country not found.")
            else:
                return r.json()
