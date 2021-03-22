import requests
from colorama import Fore
from plugin import plugin, require


@require(network=True)
@plugin("activity")
def activity(jarvis, s):
    """Tells a activity to do when you're bored, powered by www.boredapi.com"""

    req = requests.get("https://www.boredapi.com/api/activity")
    data = req.json()
    response = ""

    if data == "":
        jarvis.say("Sorry, an error occured", Fore.BLUE)
        return

    if (data.get('accessibility') < 0.4):
        response += "I can purpose something interesting but it's not easy and "
    elif (data.get('accessibility') < 0.6):
        response += "I have something easy for you and "

    if (data.get('price') == 0):
        response += "it's free, "
    elif (data.get('price') <= 0.3):
        response += "it's quite cheap, "
    elif (data.get('price') > 0.3 and data.get('price') < 0.6):
        response += "it cost a few. "
    elif (data.get('price') >= 0.6):
        response += "but it's expensive. "

    if (data.get('participants') > 1):
        response += "It's a group activity of" + str(data.get('participants')) + "participants"

    response += data.get('activity')
    jarvis.say(response, Fore.BLUE)
