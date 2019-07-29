from plugin import plugin
import os
import json

FILE_PATH = os.path.abspath(os.path.dirname(__file__))


@plugin('dial code')
class PhoneCode:
    """
    Prints the dial code of the country
    Usage: dial code <COUNTRY NAME>
        OR
           phone code <CONTRY NAME>
    """
    def __call__(self, jarvis, s):
        code = self.handle_input(s)
        if code:
            jarvis.say('Dial code is: ' + code)
        else:
            jarvis.say("Can't find code for contry: '" + s + "'")

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
