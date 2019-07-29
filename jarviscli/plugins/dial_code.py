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
        # (or False if there is no such country)
        code = self.handle_input(s)
        if code:
            jarvis.say(Fore.GREEN + 'Dial code is ' + Fore.WHITE + code)
        else:
            jarvis.say(Fore.RED + "Can't find code for country " + Fore.WHITE + "'" + s + "'")

    def handle_input(self, country):
        
        # Open the file with dial codes
        codes_file = open(os.path.join(FILE_PATH,
                                       "../data/dial_codes.json"), 'r')
                                       
        # Load json with codes from file
        data = json.loads(codes_file.read())
        codes_file.close()

        for i in data:
            if country == i["name"].lower():
                code = i["dial_code"]
                return(code)

        return(False)
