# Converts a given string to a given case.
from plugin import plugin
from colorama import Fore


@plugin("string_convert")
def string_convert(jarvis, s):
    inputString = str(
        jarvis.input(
            "Give me a string to convert to another case (supported: UPPER/lower/Title/Sentence)"
        )
    )
    jarvis.say("1. UPPER CASE")
    jarvis.say("2. lower case")
    jarvis.say("3. Title Case")
    jarvis.say("4. Sentence case")
    userCase = int(jarvis.input("Enter the number (1-4): "))
    res = ""

    if userCase == 1:
        # UPPER CASE
        res = inputString.upper()
    elif userCase == 2:
        res = inputString.lower()
    elif userCase == 3:
        res = inputString.title()
    else:
        res = inputString.capitalize()

    jarvis.say("Here is your converted sentence:")
    jarvis.say(res)
