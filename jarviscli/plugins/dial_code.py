from plugin import plugin, alias
import os
import json
from colorama import Fore

FILE_PATH = os.path.abspath(os.path.dirname(__file__))


@alias('phone code of')
@plugin('dial code of')
class DialCode:
    """
    Prints the dial code of the country
    Usage: dial code of <COUNTRY NAME>
    Alias(es): phone code of
    """
    def __call__(self, jarvis, s):
        # Call handle_input() function wich returns the code
        # (or False if no such country)
        code = self.handle_input(s)

        if code:
            jarvis.say(Fore.GREEN + 'Dial code is ' + Fore.WHITE + code)
        else:
            # Ask whether to print all available countries if False
            jarvis.say(Fore.RED + "Can't find code for country "
                                + Fore.WHITE + "'" + s + "'")
            choice = jarvis.input(Fore.GREEN + 'Print avaliable countries?'
                                      + Fore.WHITE + ' (y/N): ')

            if choice in ['y', 'Y']:
                # Open the file with dial codes
                codes_file = open(os.path.join(FILE_PATH,
                                               "../data/dial_codes.json"), 'r')

                data = json.loads(codes_file.read())

                all_countries = ''
                for i in data:
                    all_countries += i["country_name"]
                    all_countries += ' * '

                jarvis.say(all_countries)

    def handle_input(self, country):

        # Open the file with dial codes
        codes_file = open(os.path.join(FILE_PATH,
                                       "../data/dial_codes.json"), 'r')

        # Load json with codes from file
        data = json.loads(codes_file.read())
        codes_file.close()

        # Compare user's input to each "country_name" in json
        # and find necessary code
        for i in data:
            if country == i["country_name"].lower():
                code = i["dial_code"]
                return(code)

        return(False)
