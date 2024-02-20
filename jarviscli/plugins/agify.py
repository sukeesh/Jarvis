import requests
from colorama import Fore
from jarviscli import entrypoint


@entrypoint
def agify(jarvis, s):
    """Tells the age of someone based on his name, powered by www.boredapi.com"""

    if (s):
        req = requests.get("https://api.agify.io?name=" + s)
        data = req.json()
        if data == "":
            jarvis.say("Sorry, an error occured", Fore.BLUE)
            return
        response = "I think you are " + str(data.get('age'))

        jarvis.say(response, Fore.BLUE)

    else:
        jarvis.say("Please give me the name of someone", Fore.BLUE)
