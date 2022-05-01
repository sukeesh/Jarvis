from colorama import Fore
from plugin import plugin, require
import requests
import re


@require(network=True)
@plugin("name day")
class NameDay:
    """
    Name Day plugin provides information about your country's name days

    You can see today's, tomorrow's, or any other day's name day.

    You can also see the name day of a specific name.
    """
    def __call__(self, jarvis, s):
        self.jarvis = jarvis
        self.main()

    def __init__(self):
        self.jarvis = None
        self.location = ""
        self.countries = {
            "Austria": "at",
            "Bulgaria": "bg",
            "Croatia": "hr",
            "Czech Republic": "cz",
            "Denmark": "dk",
            "Estonia": "ee",
            "Finland": "fi",
            "France": "fr",
            "Germany": "de",
            "Greece": "gr",
            "Hungary": "hu",
            "Italy": "it",
            "Latvia": "lv",
            "Lithuania": "lt",
            "Poland": "pl",
            "Russia": "ru",
            "Slovakia": "sk",
            "Spain": "es",
            "Sweden": "se",
            "United States": "us"
        }

    def main(self):

        if self.location == "":
            self.get_location()
        while True:
            # main menu
            self.jarvis.say("It appears you are in " + self.location, color=Fore.BLUE)
            self.jarvis.say("1 See Today's name days")
            self.jarvis.say("2 See Tomorrow's name days")
            self.jarvis.say("3 Chose specific date")
            self.jarvis.say("4 Chose specific name")
            self.jarvis.say("5 Chose an other country")
            self.jarvis.say("6 Exit")

            # get user input
            try:
                inp = int(self.jarvis.input("Select the desired number: ", color=Fore.GREEN))
            except ValueError:
                self.jarvis.say("Please select a number")
                continue

            # handle input
            if inp == 1:
                self.today()
            elif inp == 2:
                self.tomorrow()
            elif inp == 3:
                self.specific_date()
            elif inp == 4:
                self.specific_name()
            elif inp == 5:
                self.change_country()
                continue
            elif inp == 6:
                break
            else:
                self.jarvis.say("Please select a valid number")

            # ask user if he wants to continue
            inp = self.jarvis.input("Do you want to continue? (Y/N)", color=Fore.RED)
            if inp.lower() == "n":
                break

    def get_country_code(self):
        """Return the two letter country code"""
        return self.countries[self.location]

    def get_location(self):
        """
        Get the location of the user.
        If the user is in a supported country, the country is saved in location class variable.
        otherwise, the user is asked to enter a country from the supported list.
        """
        self.jarvis.say("Getting Location ... ")
        send_url = 'http://api.ipstack.com/check?access_key=f16ebe59174140a634827d674e605350&output=json&legacy=1'
        js = requests.get(send_url).json()
        loc = js["country_name"]

        if loc in self.countries.keys():
            self.location = loc
        else:
            self.jarvis.say("It appears you are in " + loc)
            self.jarvis.say("Your Country is not supported")
            self.jarvis.say("Please chose an other country")
            self.change_country()

    def today(self):
        """
        Show the name days for today.
        """
        country_code = self.get_country_code()
        j = requests.get("https://nameday.abalin.net/api/V1/today",
                         params={"country": country_code}).json()
        names = j["nameday"][country_code]
        if names != "n/a":
            self.jarvis.say("Say some kind words to " + names)
        else:
            self.jarvis.say("No name days today in " + str(self.location))

    def tomorrow(self):
        """
        Show the name days for tomorrow.
        """
        country_code = self.get_country_code()
        j = requests.get("https://nameday.abalin.net/api/V1/tomorrow",
                         params={"country": country_code}).json()
        names = j["nameday"][country_code]
        if names != "n/a":
            self.jarvis.say("Say some kind words to " + names)
        else:
            self.jarvis.say("No name days for tomorrow in " + str(self.location))

    def specific_date(self):
        """
        Show the name days for a specific date.
        """
        country_code = self.get_country_code()
        self.jarvis.say("Please enter day/month")
        try:
            day, month = re.split(r'[ /-]+', self.jarvis.input().strip())
            self.check_if_date_is_valid(day, month)
        except ValueError:
            self.specific_date()
            return
        j = requests.get("https://nameday.abalin.net/api/V1/getdate",
                         params={"country": country_code, "day": day, "month": month}).json()
        names = j["nameday"][country_code]
        if names != "n/a":
            self.jarvis.say("Say some kind words to " + names + " on " + day + "/" + month)
        else:
            self.jarvis.say("No name days at " + day + "/" + month + " in " + self.location)

    def specific_name(self):
        """
        Show the name days for a specific name.
        """
        country_code = self.get_country_code()
        self.jarvis.say("Please enter name")
        name = self.jarvis.input().strip()
        j = requests.get("https://nameday.abalin.net/api/V1/getname",
                         params={"country": country_code, "name": name}).json()

        # the same name may have multiple name days
        if j["0"]:
            dates = ""
            for s in j["0"]:
                date = str(s["day"]) + "/" + str(s["month"]) + " "
                dates += date.strip()
            self.jarvis.say("Say some kind words to " + name + " at " + dates)
        else:
            self.jarvis.say("No name days found for " + name)

    def change_country(self):
        """
        Change the location of the user manually.
        """
        self.jarvis.say("Select your country number from the list below:")
        for i, key in enumerate(self.countries.keys(), start=1):
            self.jarvis.say(str(i) + " " + key)
        self.jarvis.say(str(len(self.countries) + 1) + " Cancel")

        while True:
            country = int(self.jarvis.input("Select your country number: "))
            if country in range(1, len(self.countries) + 2):
                break
            else:
                self.jarvis.say("Please select a valid country number")

        if country == len(self.countries) + 1:
            return
        self.location = list(self.countries.keys())[country - 1]

    def check_if_date_is_valid(self, day, month):
        """
        Check if the date taken for user is valid.
        :raise ValueError: if the date is invalid.
        """
        day = int(day)
        month = int(month)
        m31 = [1, 3, 5, 7, 8, 10, 12]
        m30 = [4, 6, 9, 11]
        if month in m31:
            if 0 > day or day > 31:
                self.jarvis.say("Please enter a valid date")
                raise ValueError
        elif month in m30:
            if 0 > day or day > 30:
                self.jarvis.say("Please enter a valid date")
                raise ValueError
        elif month == 2:
            if 0 > day or day > 29:
                self.jarvis.say("Please enter a valid date")
                raise ValueError
        else:
            self.jarvis.say("Please enter a valid date")
            raise ValueError
