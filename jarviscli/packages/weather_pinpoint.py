from colorama import Fore
from utilities.GeneralUtilities import print_say
from . import mapps
from . import umbrella


def main(memory, self, s):
    location = memory.get_data('city')  # Will return None if no value
    if location is None:
        city = mapps.get_location()['city']
        print_say("It appears you are in {CITY} Is this correct? (y/n)"
                  .format(CITY=city), self, Fore.RED)
        i = input()
        if i == 'n' or i == 'no':
            print_say("Enter Name of city: ", self)
            i = input()
            city = i
        city_found = True
        if s == 'umbrella':
            umbrella.main(str(city))
        else:
            city_found = mapps.weather(str(city))
        if city_found:
            memory.update_data('city', city)
            memory.save()
    else:
        loc = str(location)
        city = mapps.get_location()['city']
        if city != loc:
            print_say(
                "It appears you are in {CITY}. But you set your location to {LOC}" .format(
                    CITY=city, LOC=loc), self, Fore.RED)
            print_say("Do you want weather for {CITY} instead? (y/n)"
                      .format(CITY=city), self, Fore.RED)
            i = input()
            if i == 'y' or i == 'yes':
                try:
                    print_say(
                        "Would you like to set {CITY} as your new location? (y/n)" .format(
                            CITY=city), self, Fore.RED)
                    i = input()
                    if i == 'y' or i == 'yes':
                        memory.update_data('city', city)
                        memory.save()
                    if s == 'umbrella':
                        umbrella.main(city)
                    else:
                        mapps.weather(city)
                except BaseException:
                    print_say("I couldn't locate you", self, Fore.RED)
            else:
                try:
                    if s == 'umbrella':
                        umbrella.main(loc)
                    else:
                        mapps.weather(loc)
                except BaseException:
                    print_say("I couldn't locate you", self, Fore.RED)
        else:
            try:
                if s == 'umbrella':
                    umbrella.main(loc)
                else:
                    mapps.weather(loc)
            except BaseException:
                print_say("I couldn't locate you", self, Fore.RED)
