from colorama import Fore
from plugin import plugin, require
import requests


# jarvis.say(requests.get("https://nameday.abalin.net/api/V1/today").json())
# jarvis.say(requests.get("https://nameday.abalin.net/api/V1/getdate", params={"country":"gr","day":"17", "month":"3"}).json())
# jarvis.say(requests.get("https://nameday.abalin.net/api/V1/getdate", params={"country":"tr","day":"17", "month":"3"}).json())
# tomorrow
# name day of alex

@require(network=True)
@plugin("name day")
class NameDay:
    def __call__(self, jarvis, s):
        self.main(jarvis)

    def __init__(self):
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

    def main(self, jarvis):

        if self.location == "":
            self.get_location(jarvis)
        while True:
            jarvis.say("It appears you are in " + self.location, color=Fore.BLUE)
            jarvis.say("1 See Today's name days")
            jarvis.say("2 See Tomorrow's name days")
            jarvis.say("3 Chose specific date")
            jarvis.say("4 Chose specific name")
            jarvis.say("5 Chose an other country")
            jarvis.say("6 Exit")
            try:
                inp = int(jarvis.input("Select the desired number: ", color=Fore.GREEN))
            except ValueError:
                jarvis.say("Please select a number")
                continue

            if inp == 1:
                self.today(jarvis)
            elif inp == 2:
                self.tomorrow(jarvis)
            elif inp == 3:
                self.specific_date(jarvis)
            elif inp == 4:
                self.specific_name(jarvis)
            elif inp == 5:
                self.change_country(jarvis)
            elif inp == 6:
                break
            else:
                jarvis.say("Please select a valid number")

            inp = jarvis.input("Do you want to continue? (Y/N)", color=Fore.RED)
            if inp.lower() == "n":
                break

    def get_country_code(self):
        return self.countries[self.location]

    def get_location(self, jarvis):
        jarvis.say("Getting Location ... ")
        send_url = 'http://api.ipstack.com/check?access_key=f16ebe59174140a634827d674e605350&output=json&legacy=1'
        js = requests.get(send_url).json()
        loc = js["country_name"]

        if loc in self.countries.keys():
            self.location = loc
        else:
            jarvis.say("It appears you are in " + loc)
            jarvis.say("Your Country is not supported")
            jarvis.say("Please chose an other country")
            self.change_country()

    def today(self, jarvis):
        country_code = self.get_country_code()
        j = requests.get("https://nameday.abalin.net/api/V1/today",
                         params={"country": country_code}).json()
        names = j["nameday"][country_code]
        if names != "n/a":
            jarvis.say("Say some kind words to " + names)
        else:
            jarvis.say("No name days today")

    def tomorrow(self, jarvis):
        country_code = self.get_country_code()
        j = requests.get("https://nameday.abalin.net/api/V1/tomorrow",
                         params={"country": country_code}).json()
        names = j["nameday"][country_code]
        if names != "n/a":
            jarvis.say("Say some kind words to " + names)
        else:
            jarvis.say("No name days for tomorrow")

    def specific_date(self, jarvis):
        country_code = self.get_country_code()
        jarvis.say("Please enter day/month")
        day, month = jarvis.input().strip().split()
        j = requests.get("https://nameday.abalin.net/api/V1/getdate",
                         params={"country": country_code, "day": day, "month": month}).json()
        names = j["nameday"][country_code]
        if names != "n/a":
            jarvis.say("Say some kind words to " + names)
        else:
            jarvis.say("No name days at " + str(month) + "/" + str(day))

    def specific_name(self, jarvis):
        country_code = self.get_country_code()
        jarvis.say("Please enter name")
        name = jarvis.input().strip()
        j = requests.get("https://nameday.abalin.net/api/V1/getname",
                         params={"country": country_code, "name": name}).json()
        # day = j["0"]["day"]
        # month = j["0"]["month"]
        if j["0"]:
            dates = ""
            for s in j["0"]:
                date = str(s["day"]) + "/" + str(s["month"]) + " "
                dates += date
            jarvis.say("Say some kind words to " + name + " at " + dates)
        else:
            jarvis.say("No name days at found for " + name)

    def change_country(self, jarvis):
        jarvis.say("Select your country number from the list below:")
        for i, key in enumerate(self.countries.keys(), start=1):
            jarvis.say(str(i) + " " + key)

        while True:
            country = int(jarvis.input("Select your country number: "))
            if country in range(1, len(self.countries) + 1):
                break
            else:
                jarvis.say("Please select a valid country number")

        self.location = list(self.countries.keys())[country - 1]
