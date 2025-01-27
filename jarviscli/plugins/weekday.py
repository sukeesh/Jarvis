from plugin import alias, plugin
from colorama import Fore

def dayofweek(d, m, y):
    """
    Calculates the weekday for any date and returns 0 to Sunday, 1 to Monday...
    """
    # code from https://www.geeksforgeeks.org/find-day-of-the-week-for-a-given-date/
    t = [ 0, 3, 2, 5, 0, 3,
          5, 1, 4, 6, 2, 4 ]
    y -= m < 3
    return (( y + int(y / 4) - int(y / 100)
             + int(y / 400) + t[m - 1] + d) % 7)

@alias("weekday")
@plugin("day of the week")
def weekday(jarvis, s):
    """
    Says what weekday any date is.
    """
    m_with_31 = [1,3,5,7,8,10,12]
    weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    if s == "":
        s = jarvis.input("Tell me any date using the dd/mm/aaaa format:\n")

    # wrong format error
    s_split = s.split("/")
    if(len(s)<3):
        jarvis.say("Something is worng with this date.\n Try to use \"weekday dd/mm/aaaa\"", Fore.ORANGE)
        return

    # splitting data and turning into int
    d = int(s_split[0])
    m = int(s_split[1])
    a = int(s_split[2])

    if a<1:
        jarvis.say("Sorry, but I only can the the day of the week from year 1 onwards! :(", Fore.RED)
        return

    if m<1 or m>12:
        jarvis.say("Months go from 1 to 12! Remember to use dd/mm/aaaa format.", Fore.RED)
        return

    if d<1 or d>31:
        jarvis.say("Days go from 1 to 31! Remember to use dd/mm/aaaa format.", Fore.RED)
        return

    if d==31 and m not in m_with_31:
        jarvis.say(f"Month {m} doen't have 31 days!", Fore.RED)
        return

    if m==2 and d>29:
        jarvis.say("Month 2 have only 28 or 29 days!", Fore.RED)
        return

    # calculate weekday
    week_day = dayofweek(d, m, a)

    jarvis.say(f"{s} is a {weekdays[week_day]}!", Fore.GREEN)

    return
