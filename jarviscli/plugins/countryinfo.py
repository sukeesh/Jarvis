from plugin import plugin, require
import requests


@require(network=True)
@plugin('countryinfo')
class country_info:
    """
    Welcome to the Countryinfo plugin documentation! Here you will be able
    to find all the functionalities of the plugin.
    Usage: Type countryinfo and follow the instructions.
    This plugin gives you several important details corresponding to country which is asked as an input
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
                "Enter the name of the country or type exit to leave: ")
            if country == '':
                jarvis.say("Please enter valid input.")
            elif country == 'exit':
                return
            else:
                url = "https://restcountries.eu/rest/v2/name/%s?fullText=true" % country
                r = requests.get(url)
                if isinstance(r.json(), dict):
                    jarvis.say("Country not found.")
                else:
                    return r.json()

    def country_info(self, jarvis, country_fetch):
        capital = country_fetch[0]["capital"]
        calling_code = country_fetch[0]["callingCodes"][0]
        population = country_fetch[0]["population"]
        region = country_fetch[0]["region"]
        currency = country_fetch[0]["currencies"][0]["name"]
        currency_symbol = country_fetch[0]["currencies"][0]["symbol"]
        time_zone = country_fetch[0]["timezones"][0]

        print()
        jarvis.say("Capital: " + capital)
        jarvis.say("Calling Code: " + calling_code)
        jarvis.say("Currency: " + currency)
        jarvis.say("Currency Symbol: " + currency_symbol)
        jarvis.say("Population: " + str(population))
        jarvis.say("Region: " + region)
        jarvis.say("Time Zone: " + time_zone)

        return
