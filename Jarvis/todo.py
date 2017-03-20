# -*- coding: utf-8 -*-
import os
import sys
import json

from datetime import datetime as dt
from datetime import date, time, timedelta
from dateutil.relativedelta import relativedelta
import re

from colorama import init
from colorama import Fore, Back, Style

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, dt):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

def writeToFile():
    with open("todolist.txt", "w+") as f:
        json.dump(todoList, f, default=json_serial)

def _print(data):
    x = 0
    for l in data:
        if 'priority' in l and l['priority'] >= 50:
            sys.stdout.write(Fore.YELLOW)
        if 'priority' in l and l['priority'] >= 100:
            sys.stdout.write(Fore.RED)
        print("<{2}> {0} [{1}%]".format(l['name'], l['complete'], x) + Fore.RESET)
        if 'due' in l:
            print("\tDue at {0}".format(l['due']))
        if 'comment' in l:
            print("\t{0}".format(l['comment']))
        x += 1

def sort(data):
    return sorted(data, key = lambda k: (-k['priority'] if 'priority' in k else 0, k['complete']))

def parseNumber(string):
    ret = {'skip':1, 'value':1}
    try:
        ret['value'] = int(string)
    except ValueError:
        #TODO Turn words into integers/floats
        print("number words not yet supported")
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
            tmp = parseNumber(d)
            deltaValue = tmp['value']
            parseDeltaUnit = tmp['skip']
            parseDeltaValue = False
        elif parseDeltaUnit:
            if parseDeltaUnit > 1:
                parseDeltaUnit += 1
            elif "year" in d:
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
            else:
                print("Missing time unit")

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

def todoHandler(data):
    global todoList
    if "add" in data:
        data = data.replace("add", "", 1)
        if "comment" in data:
            data = data.replace("comment", "", 1)
            words = data.split()
            index = int(words[0])
            if(index<0 or index>=len(todoList['items'])):
                print("No such todo")
                return
            todoList['items'][index]['comment'] = " ".join(words[1:])
        elif "due" in data or "due date" in data:
            data = data.replace("due date", "", 1)
            data = data.replace("due", "", 1)
            words = data.split()
            index = int(words[0])
            if(index<0 or index>=len(todoList['items'])):
                print("No such todo")
                return
            todoList['items'][index]['due'] = parseDate(" ".join(words[1:]))
        else:
            data = " ".join(data.split())
            newItem = {'complete':0}
            if " - " in data:
                parts = data.split(" - ")
                newItem['name'] = parts[0]
                newItem['comment'] = parts[1]
            else:
                newItem['name'] = data
            todoList['items'].append(newItem)
    elif "remove" in data:
        data = data.replace("remove", "", 1)
        index = int(data.split()[0])
        if(index<0 or index>=len(todoList['items'])):
            print("No such todo")
            return
        todoList['items'].remove(todoList['items'][index])
    elif "priority" in data:
        data = data.replace("priority", "", 1)
        if "critical" in data:
            data = data.replace("critical", "", 1)
            priority = 100
        elif "high" in data:
            data = data.replace("high", "", 1)
            priority = 50
        elif "normal" in data:
            data = data.replace("normal", "", 1)
            priority = 0
        else:
            words = data.split()
            priority = int(words[1])
        words = data.split()
        index = int(words[0])
        if(index<0 or index>=len(todoList['items'])):
            print("No such todo")
            return
        todoList['items'][index]['priority'] = priority
    elif "complete" in data:
        data = data.replace("complete", "", 1)
        words = data.split()
        index = int(words[0])
        if(index<0 or index>=len(todoList['items'])):
            print("No such todo")
            return
        complete = 100
        if words[1]:
            complete = int(words[1])
        todoList['items'][index]['complete'] = complete
    elif "help" in data:
        print(Fore.GREEN + "Commands: {add <todo description>, remove <index>, complete <index> [<completion>], priority <index> [<level>]}" + Fore.RESET)
        return

    todoList['items'] = sort(todoList['items'])
    _print(todoList['items'])
    writeToFile()

todoList = {}
todoList['items'] = []
if not os.path.exists("todolist.txt"):
    writeToFile()
else:
    with open("todolist.txt", "r+") as f:
        todoList = json.load(f)
        todoList['items'] = sort(todoList['items'])

