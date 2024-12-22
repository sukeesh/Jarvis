from colorama import Fore
from utilities.GeneralUtilities import print_say
from . import mapps
from . import umbrella

def handle_new_location(self, city):
    print_say("Enter Name of city: ", self)
    city = input()
    return city

def handle_location_change(memory, self, new_city, old_location):
    print_say(
        f"It appears you are in {new_city}. But you set your location to {old_location}", 
        self, Fore.RED)
    print_say(f"Do you want weather for {new_city} instead? (y/n)", self, Fore.RED)
    if input().lower() in ['y', 'yes']:
        if ask_set_new_location(self, new_city):
            memory.update_data('city', new_city)
            memory.save()
        return new_city
    return old_location

def ask_set_new_location(self, city):
    print_say(f"Would you like to set {city} as your new location? (y/n)", self, Fore.RED)
    return input().lower() in ['y', 'yes']

def get_weather_for_city(self, city, s):
    try:
        if s == 'umbrella':
            umbrella.main(city)
        else:
            return mapps.weather(city)
        return True
    except BaseException:
        print_say("I couldn't locate you", self, Fore.RED)
        return False

def main(memory, self, s):
    location = memory.get_data('city')
    if location is None:
        city = mapps.get_location()['city']
        print_say(f"It appears you are in {city} Is this correct? (y/n)", self, Fore.RED)
        if input().lower() in ['n', 'no']:
            city = handle_new_location(self, city)
        
        if get_weather_for_city(self, city, s):
            memory.update_data('city', city)
            memory.save()
    else:
        current_city = mapps.get_location()['city']
        if current_city != location:
            city = handle_location_change(memory, self, current_city, location)
        else:
            city = location
        get_weather_for_city(self, city, s)
