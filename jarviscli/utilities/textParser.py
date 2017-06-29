# -*- coding: utf-8 -*-

from datetime import datetime as dt
from datetime import date, time, timedelta
from dateutil.relativedelta import relativedelta
import re

def parseNumber(string, numwords = {}):
    """
    Parse the given string to an integer.

    This supports pure numerals with or without ',' as a separator between digets.
    Other supported formats include literal numbers like 'four' and mixed numerals
    and literals like '24 thousand'.
    :return: (skip, value) containing the number of words separated by whitespace,
             that were parsed for the number and the value of the integer itself.
    """
    if not numwords:
        units = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen" ]
        tens = ["", "", "twenty", "thirty", "fourty", "fifty", "sixty", "seventy", "eighty", "ninety"]
        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):    numwords[word] = (1, idx)
        for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    skip = 0
    value = 0
    elements = string.replace(",", "").split()
    current = 0
    for d in elements:
        number = d.split("-")
        for word in number:
            if word not in numwords:
                try:
                    scale, increment = (1, int(word))
                except ValueError:
                    value += current
                    return (skip, value)
            else:
                scale, increment = numwords[word]
                if not current and scale > 100:
                    current = 1
            current = current * scale + increment
            if scale > 100:
                value += current
                current = 0
        skip += 1
    value += current
    return (skip, value)
    
def parseDate(string):
    """
    Parse the given string for a date or timespan.

    The number for a timespan can be everything supported by parseNumber().

    Supported date formats:
        2017-03-22 and 17-03-22
        22.03.2017 and 22.03.17
    Supported time formats:
        17:30
        5:30PM
    Supported timespan formats:
        in one second/minute/hour/day/week/month/year
        next monday
    :return: (skip, time) containing the number of words separated by whitespace,
             that were parsed for the date and the date itself as datetime.
    """
    elements = string.split()

    parseDay = False
    parseDeltaValue = False
    parseDeltaUnit = 0
    deltaValue = 0
    retDate = dt.now().date()
    retTime = dt.now().time()
    skip = 0
    for index, d in enumerate(elements):
        if parseDay:
            d += dt.today().strftime(" %Y %W")
            try:
                retDate = dt.strptime(d, "%a %Y %W").date()
            except ValueError:
                try:
                    retDate = dt.strptime(d, "%A %Y %W").date()
                except ValueError:
                    parseDay = False
                    break
            if retDate <= dt.now().date():
                retDate += timedelta(days = 7)
            parseDay = False
        elif parseDeltaValue:
            parseDeltaUnit, deltaValue = parseNumber(" ".join(elements[index:]))
            parseDeltaValue = False
        elif parseDeltaUnit:
            newTime = dt.combine(retDate, retTime)
            if "year" in d:
                retDate += relativedelta(years = deltaValue)
            elif "month" in d:
                retDate += relativedelta(months = deltaValue)
            elif "week" in d:
                retDate += timedelta(weeks = deltaValue)
            elif "day" in d:
                retDate += timedelta(days = deltaValue)
            elif "hour" in d:
                newTime += timedelta(hours = deltaValue)
                retDate = newTime.date()
                retTime = newTime.time()
            elif "minute" in d:
                newTime += timedelta(minutes = deltaValue)
                retDate = newTime.date()
                retTime = newTime.time()
            elif "second" in d:
                newTime += timedelta(seconds = deltaValue)
                retDate = newTime.date()
                retTime = newTime.time()
            elif parseDeltaUnit == 1:
                print("Missing time unit")
            parseDeltaUnit -= 1

        elif re.match("^[0-9]{2}-[0-1][0-9]-[0-3][0-9]$", d):
            retDate = dt.strptime(d, "%y-%m-%d").date()
        elif re.match("^[1-9][0-9]{3}-[0-1][0-9]-[0-3][0-9]$", d):
            retDate = dt.strptime(d, "%Y-%m-%d").date()
        elif re.match("^[0-3][0-9]\.[0-1][0-9]\.[0-9]{2}$", d):
            retDate = dt.strptime(d, "%d.%m.%y").date()
        elif re.match("^[0-3][0-9]\.[0-1][0-9]\.[1-9][0-9]{3}$", d):
            retDate = dt.strptime(d, "%d.%m.%Y").date()

        elif re.match("^[0-1][0-9]:[0-5][0-9][AP]M$", d):
            retTime = dt.strptime(d, "%I:%M%p").time()
        elif re.match("^[1-9]:[0-5][0-9][AP]M$", d):
            retTime = dt.strptime("0" + d, "%I:%M%p").time()
        elif re.match("^[0-2][0-9]:[0-5][0-9]$", d):
            retTime = dt.strptime(d, "%H:%M").time()
        elif re.match("^[1-9]:[0-5][0-9]$", d):
            retTime = dt.strptime("0" + d, "%H:%M").time()

        elif d == "next":
            parseDay = True
        elif d == "in" or d == "and":
            parseDeltaValue = True
        else:
            break
        skip += 1
    return (skip, dt.combine(retDate, retTime))
