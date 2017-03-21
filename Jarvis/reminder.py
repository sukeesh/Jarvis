# -*- coding: utf-8 -*-
import os
import json

from datetime import datetime as dt
from datetime import date, time, timedelta
from dateutil.relativedelta import relativedelta
import re

from colorama import init
from colorama import Fore, Back, Style

from fileHandler import writeFile, readFile, str2date

def parseNumber(string, numwords = {}):
    if not numwords:
        units = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen" ]
        tens = ["", "", "twenty", "thirty", "fourty", "fifty", "sixty", "seventy", "eighty", "ninety"]
        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):    numwords[word] = (1, idx)
        for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    ret = {'skip':0, 'value':0}
    elements = string.replace(",", "").split()
    current = 0
    for d in elements:
        number = d.split("-")
        for word in number:
            if word not in numwords:
                try:
                    scale, increment = (1, int(word))
                except ValueError:
                    ret['value'] += current
                    return ret
            else:
                scale, increment = numwords[word]
                if not current and scale > 100:
                    current = 1
            current = current * scale + increment
            if scale > 100:
                ret['value'] += current
                current = 0
        ret['skip'] += 1
    ret['value'] += current
    return ret
    
def parseDate(data):
    elements = data.split()

    parseDay = False
    parseDeltaValue = False
    parseDeltaUnit = 0
    deltaValue = 0
    retDate = dt.now().date()
    retTime = time(23, 59, 59)
    for index, d in enumerate(elements):
        if parseDay:
            d += dt.today().strftime(" %Y %W")
            try:
                retDate = dt.strptime(d, "%a %Y %W").date()
            except ValueError:
                try:
                    retDate = dt.strptime(d, "%A %Y %W").date()
                except ValueError:
                    print("Could not parse word: {0}".format(d))
                    parseDay = False
                    continue
            if retDate <= dt.now().date():
                retDate += timedelta(days = 7)
            parseDay = False
        elif parseDeltaValue:
            tmp = parseNumber(" ".join(elements[index:]))
            deltaValue = tmp['value']
            parseDeltaUnit = tmp['skip']
            parseDeltaValue = False
        elif parseDeltaUnit:
            if "year" in d:
                retDate += relativedelta(years = deltaValue)
            elif "month" in d:
                retDate += relativedelta(months = deltaValue)
            elif "week" in d:
                retDate += timedelta(weeks = deltaValue)
            elif "day" in d:
                retDate += timedelta(days = deltaValue)
            elif "hour" in d:
                newTime = dt.now() + timedelta(hours = deltaValue)
                retDate = newTime.date()
                retTime = newTime.time()
            elif "minute" in d:
                newTime = dt.now() + timedelta(minutes = deltaValue)
                retDate = newTime.date()
                retTime = newTime.time()
            elif "second" in d:
                newTime = dt.now() + timedelta(seconds = deltaValue)
                retDate = newTime.date()
                retTime = newTime.time()
            elif parseDeltaUnit == 1:
                print("Missing time unit")
            parseDeltaUnit -= 1

        elif re.match("^[0-9]{2}-[0-1][0-9]-[0-3][0-9]", d):
            retDate = dt.strptime(d, "%y-%m-%d").date()
        elif re.match("^[1-9][0-9]{3}-[0-1][0-9]-[0-3][0-9]", d):
            retDate = dt.strptime(d, "%Y-%m-%d").date()
        elif re.match("^[0-3][0-9]-[0-1][0-9]-[0-9]{2}", d):
            pretDate = dt.strptime(d, "%d.%m.%y").date()
        elif re.match("^[0-3][0-9]-[0-1][0-9]-[1-9][0-9]{3}", d):
            retDate = dt.strptime(d, "%d.%m.%Y").date()

        elif re.match("^[0-1][0-9]:[0-5][0-9][AP]M", d):
            retTime = dt.strptime(d, "%I:%M%p").time
        elif re.match("^[0-2][0-9]:[0-5][0-9]", d):
            retTime = dt.strptime(d, "%H:%M").time

        elif d == "next":
            parseDay = True
        elif d == "in":
            parseDeltaValue = True
        else:
            print("Unknown Format: {0}".format(d))
            continue
    return dt.combine(retDate, retTime)
        
def sort(data):
    return sorted(data, key = lambda k: (k['time']))

def addReminder(name, time, hidden = True):
    newItem = {'name': name, 'time': time, 'hidden': hidden}
    reminderList['items'].append(newItem)
    reminderList['items'] = sort(reminderList['items'])
    writeFile("reminderlist.txt", reminderList)

def removeReminder(name):
    for index, e in enumerate(reminderList['items']):
        if name == e['name']:
            reminderList['items'].remove(reminderList['items'][index])
            break;

def handle(data):
    if "add" in data:
        newItem = {}
        data = data.replace("add", "", 1)
        words = data.split()
        addReminder(name=words[0], time=parseDate(" ".join(words[1:])), hidden=False)
    elif "remove" in data:
        data = data.replace("remove", "", 1)
        index = parseNumber(data)['value'] - 1
        reminderList['items'].remove(reminderList['items'][index])
        writeFile("reminderlist.txt", reminderList)
    elif "print" in data or "list" in data:
        for index, e in enumerate(reminderList['items']):
            if not e['hidden']:
                print("<{0}> {2}: {1}".format(index + 1, e['time'], e['name']))

reminderList = readFile("reminderlist.txt", {'items':[]})
reminderList['items'] = sort(reminderList['items'])
for e in reminderList['items']:
    e['time'] = str2date(e['time'])

