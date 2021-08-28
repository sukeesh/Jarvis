import webbrowser

from colorama import Fore

from plugin import alias, plugin, require

# TODO near city


@require(network=True)
@plugin('near')
def near(jarvis, s):
    """
    Jarvis can find what is near you!
    -- Examples:
        restaurants near me
    """
    word_list = data.split()
    try:
        things = " ".join(word_list[0:wordIndex(data, "|")])
    except ValueError:
        print('Value error')
        return False

    jarvis.say("Hold on!, I'll show {THINGS} near you".format(THINGS=things), color=Fore.Green)
    url = "https://www.google.com/maps/search/{0}/@{1},{2}".format(
        things,
        jarvis.get_location(jarvis.LocationFields.LATITUDE),
        jarvis.get_location(jarvis.LocationFields.LONGITUDE))
    webbrowser.open(url)
