from plugin import plugin
import requests


@plugin('countryinfo')
class country_info:
    """
    Welcome to the Capitals plugin documentation! Here you will be able
    to find all the functionalities of the plugin.
    Usage: Type capitals and follow the instructions.
    This plugin gives you capital corresponding to country as well as country corresponding
    to capital.
    Please enter country name in smallcase
    Go on explore your information!!
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
        country = input('Enter the name of country: ')
        url = "https://restcountries.eu/rest/v2/name/%s?fullText=true" % country
        r = requests.get(url)
        valid_input = False
        while not valid_input:
            if type(r.json()) == dict:
                jarvis.say(
                    "Please Enter A Valid Input or else type exit to leave")
                country = input(
                    'Enter the name of country or type exit to leave: ')
                print()
                if country == 'exit':
                    break
                else:
                    url = "https://restcountries.eu/rest/v2/name/%s?fullText=true" % country
                    r = requests.get(url)
                    continue
            else:
                valid_input = True
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
        print("Capital: " + capital)
        print("Calling Code: " + calling_code)
        print("Currency: " + currency)
        print("Currency Symbol: " + currency_symbol)
        print("Population: " + str(population))
        print("Region: " + region)
        print("Time Zone: " + time_zone)

        return
