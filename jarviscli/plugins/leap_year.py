from plugin import plugin


@plugin("leap year")
def leap_year(jarvis, s):
    if s == "":
        s = jarvis.input("Enter a year: ")
    try:
        year = int(s)
    except ValueError:
        jarvis.say(
            "Wrong input. Please make sure you just enter an integer e.g. '2012'."
        )
        return
    else:
        if (
            (year % 400 == 0)
            and (year % 100 == 0)
            or (year % 4 == 0)
            and (year % 100 != 0)
        ):
            jarvis.say(f"{year} is a leap year.")
        else:
            jarvis.say(f"{year} is not a leap year.")
