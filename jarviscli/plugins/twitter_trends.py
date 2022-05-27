# -*- coding: utf-8 -*-
"""Twitter Trends plugin.

    This plugin prints a list of countries with their unique id and returns
    the top 10 trends in Twitter for this specific country.

    Typical usage example:

    >twitter trends
    >number_of_country

    @Author: Leonidha Mara @leonidhaMara & Emmanouil Manousakis @manousakis01
    @Date: 7th May, 2022
"""
from colorama import Fore
from plugin import plugin, require, alias
import requests
import json

@alias("trendtwit")
@require(network=True)
@plugin("twitter trends")
class TwitterTrends:
    def __call__(self, jarvis, s):
        self.jarvis = jarvis
        if self.countries is None:
            self.countries = self.available_countries()
        self.main()

    def __init__(self):
        self.countries = None
        self.exit_msg = "exit"

    def main(self):
        self.display_countries()
        self.jarvis.say("To exit enter word 'exit'", color=Fore.YELLOW)
        while True:
            country_code = self.get_country()
            if self.is_exit_input(country_code):
                break
            retrivied_trends = self.get_trends_from(country_code)
            self.display_trends(retrivied_trends)
            if self.is_end():
                break

    def is_end(self):
        inp = self.jarvis.input(
            "Do you want to continue? (Y/N) ", color=Fore.RED)
        if inp.lower() == "n":
            return True

    def is_out_of_range(self, x: int) -> bool:
        upper_bound = len(self.countries) - 1
        return (True if (x > upper_bound or x < 0) else False)

    def available_countries(self):
        """
        Return a dictionary of the supported countries.
        Key: number of country,
        Value: [country name, country url suffix]
        """
        URL = "http://api-twitter-trends.herokuapp.com/location"
        json_text = self.get_json(URL)
        countries_response = json_text["data"]
        countries = dict()
        # add countries
        for key, country in enumerate(countries_response):
            countries[key] = [country["location_path"],
                              country["location_url"]]
        # add worldwide option in the end
        countries[len(countries_response)] = ["worldwide", "/trends?location="]
        return countries

    def get_json(self, URL: str):
        """
        Return data from given url in json format
        """
        try:
            response = requests.get(URL)
        except Exception:
            self.jarvis.say(
                "Can not reach URL for the moment.")
        return json.loads(response.text)

    def get_country(self):
        """
        Get user input and validate it.
        Input must be a number that corresponds to a country.
        """
        country_code = None
        # Until country code is valid
        while not country_code:
            try:
                country_code = self.jarvis.input(
                    "Choose country: ", color=Fore.GREEN)
                if self.is_valid_input(int(country_code)):
                    raise ValueError
            except ValueError:
                if self.is_exit_input(country_code):
                    return 'exit'
                self.jarvis.say(
                    f"Please select a number (0 - {len(self.countries) - 1})", color=Fore.YELLOW)
                country_code = None
        return int(country_code)

    def is_exit_input(self, input):
        if (type(input) == str and input.lower() == "exit"):
            return True

    def is_valid_input(self, input):
        if type(input) == int and self.is_out_of_range(input):
            return True

    def get_trends_from(self, country: int):
        """
        Get the top 10 Twitter trends of the given country.
        """
        URL = f"https://api-twitter-trends.herokuapp.com{self.countries[country][1]}"
        json_text = self.get_json(URL)
        trends = list()
        # zero stands for the latest trends ranking
        trends_info = json_text["data"]["trends"][0]["data"]
        for trend in trends_info:
            name = trend["name"]
            tweet_count = "-"
            if trend["tweet_count"]:
                tweet_count = trend["tweet_count"]
            trends.append([name, tweet_count])
        return trends

    def display_countries(self):
        """
        Display available countries to the user.
        """
        # order in the list
        country_name_position = 0
        for country_key in self.countries:
            self.jarvis.say(
                f"{country_key:{2}}{'.':{2}}{self.countries[country_key][country_name_position].upper()}")

    def display_trends(self, trends):
        self.jarvis.say(f"     {'Trend':{24}}{'Tweets':{23}}")
        for i, v in enumerate(trends):
            self.jarvis.say(f"{i + 1:{2}}{'.':{3}}{v[0]:{25}}{v[1]:{25}}")
