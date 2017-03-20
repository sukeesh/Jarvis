# -*- coding: utf-8 -*-
import os
import sys
import json

from datetime import datetime as dt
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
    
def parseDate(data):
    elements = data.split()
    parseString = ""
    dateString = ""
    hasDate = False
    for d in elements:
        if re.match("^[0-9]{2}-[0-1][0-9]-[0-3][0-9]", d):
            parseString += "%y-%m-%d "
            hasDate = True
        elif re.match("^[1-9][0-9]{3}-[0-1][0-9]-[0-3][0-9]", d):
            parseString += "%Y-%m-%d "
            hasDate = True
        elif re.match("^[0-3][0-9]-[0-1][0-9]-[0-9]{2}", d):
            parseString += "%d.%m.%y "
            hasDate = True
        elif re.match("^[0-3][0-9]-[0-1][0-9]-[1-9][0-9]{3}", d):
            parseString += "%d.%m.%Y "
            hasDate = True

        elif re.match("^[0-1][0-9]:[0-5][0-9][AP]M", d):
            parseString += "%I:%M%p "
        elif re.match("^[0-2][0-9]:[0-5][0-9]", d):
            parseString += "%H:%M "

        else:
            print("Unknown Format: {0}".format(d))
            continue
        dateString += d + " "
    if not hasDate:
        dateString += dt.today().strftime("%Y-%m-%d")
        parseString += "%Y-%m-%d"
    try:
        return dt.strptime(dateString, parseString)
    except ValueError:
        print(Fore.RED + "Date or time out of Range." + Fore.RESET)
        return dt.today()

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

