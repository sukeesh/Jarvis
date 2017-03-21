# -*- coding: utf-8 -*-
import os
import json

from datetime import datetime as dt
from datetime import date, time, timedelta
from dateutil.relativedelta import relativedelta
from uuid import uuid4
from threading import Timer
from gi.repository import Notify
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
    skip += current
    return (skip, value)
    
def parseDate(data):
    elements = data.split()

    parseDay = False
    parseDeltaValue = False
    parseDeltaUnit = 0
    deltaValue = 0
    retDate = dt.now().date()
    retTime = time(23, 59, 59)
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
                    print("Could not parse word: {0}".format(d))
                    parseDay = False
                    break
            if retDate <= dt.now().date():
                retDate += timedelta(days = 7)
            parseDay = False
        elif parseDeltaValue:
            parseDeltaUnit, deltaValue = parseNumber(" ".join(elements[index:]))
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
            break
        skip += 1
    return (skip, dt.combine(retDate, retTime))
        
def sort(data):
    return sorted(data, key = lambda k: (k['time']))

def showAlarm(notification, name):
    print(Fore.BLUE + name + Fore.RESET)
    notification.show()

def addReminder(name, time, uuid, hidden = True, body = '', urgency=Notify.Urgency.LOW):
    waitTime = time - dt.now()
    n = Notify.Notification.new(name, body)
    n.set_urgency(urgency)
    timerList[uuid] = Timer(waitTime.total_seconds(), showAlarm, [n, name])
    timerList[uuid].start()
    print("Reminder in {} seconds".format(waitTime.total_seconds()))
    newItem = {'name':name, 'time':time, 'hidden':hidden, 'uuid':uuid}
    reminderList['items'].append(newItem)
    reminderList['items'] = sort(reminderList['items'])
    writeFile("reminderlist.txt", reminderList)

def removeReminder(uuid):
    if uuid in timerList:
        timerList[uuid].cancel()
        timerList.pop(uuid)
        for index, e in enumerate(reminderList['items']):
            if uuid == e['uuid']:
                reminderList['items'].remove(reminderList['items'][index])
                break;

def handle(data):
    if "add" in data:
        data = data.replace("add", "", 1)
        skip, time = parseDate(data)
        if skip:
            addReminder(name=" ".join(data.split()[skip:]), time=time, hidden=False, uuid=uuid4().hex)
    elif "remove" in data:
        data = data.replace("remove", "", 1)
        skip, number = parseNumber(data)
        if skip:
            index = number - 1
            if index >= 0 and index < len(reminderList['items']):
                removeReminder(reminderList['items'][index]['uuid'])
    elif "print" in data or "list" in data:
        for index, e in enumerate(reminderList['items']):
            if not e['hidden']:
                print("<{0}> {2}: {1}".format(index + 1, e['time'], e['name']))

def quit():
    for e, v in timerList.iteritems():
        v.cancel()

timerList = {}
reminderList = readFile("reminderlist.txt", {'items':[]})
reminderList['items'] = sort(reminderList['items'])
for e in reminderList['items']:
    e['time'] = str2date(e['time'])
    waitTime = e['time'] - dt.now()
    n = Notify.Notification.new(e['name'])
    n.set_urgency(Notify.Urgency.LOW)
    timerList[e['uuid']] = Timer(waitTime.total_seconds(), showAlarm, [n, e['name']])
    timerList[e['uuid']].start()

Notify.init("Jarvis")
notification = Notify.Notification.new("What can i do for you?")
notification.show()

