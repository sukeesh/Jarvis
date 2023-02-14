from plugin import plugin


@plugin("leap year")
def leap_year(jarvis, s):
    leap = False
    from collections import namedtuple
    year = int(input("Enter a year: ").strip())
    try:
        year = int(year)
    except:
        jarvis.say('Wrong input. Please make sure you just enter an integer e.g. \'2012\'.')

    if (year % 400 == 0) and (year % 100 == 0) or (year % 4 ==0) and (year % 100 != 0):
        leap = True
    if leap:
        jarvis.say(str(year) + ' is a leap year.')
    else:
        jarvis.say(str(year) + ' is not a leap year.')
    

