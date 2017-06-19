from utilities.GeneralUtilities import print_say
from colorama import Fore

def main(self, s):
    cmd_key_words = ['check', 'weather', 'forecast', 'in', 'for']
    cmd_words = s.strip().split()
    # location will be defined by the words given that are not the key words
    location = ' '.join(filter(lambda word: word.lower() not in cmd_key_words, cmd_words)).strip()

    # if no location is given, use the current location
    if not location:
        print_say("Weather forecast in the current location for the next 7 days.", self, Fore.BLUE)
        return

    # otherwise use the location given
    print_say("Weather forecast in {} for the next 7 days.".format(location), self, Fore.BLUE)
