# -*- coding: utf-8 -*-
import os
import sys
import json

from datetime import datetime as dt
import uuid

from reminder import parseNumber, parseDate, addReminder, removeReminder
from fileHandler import writeFile, readFile, str2date

from colorama import init
from colorama import Fore, Back, Style

def printItem(item, index):
    if 'priority' in item and item['priority'] >= 50:
        sys.stdout.write(Fore.YELLOW)
    if 'priority' in item and item['priority'] >= 100:
        sys.stdout.write(Fore.RED)
    print("<{2}> {0} [{1}%]".format(item['name'], item['complete'], index) + Fore.RESET)
    if not isinstance(item['uuid'], uuid.UUID):
        item['uuid'] = uuid.UUID(item['uuid'])
    if 'due' in item:
        if not isinstance(item['due'], dt):
            item['due'] = str2date(item['due'])
        if item['due'] < dt.now():
            sys.stdout.write(Fore.RED)
        print("\tDue at {0}".format(item['due'].strftime("%Y-%m-%d %H:%M:%S")) + Fore.RESET)
    if 'comment' in item:
        print("\t{0}".format(item['comment']))

def _print(data, index = ""):
    for x, element in enumerate(data):
        px = index + "{}".format(x + 1)
        printItem(element, px)
        if 'items' in element:
            _print(element['items'], px + ".")

def sort(data):
    for l in data:
        if 'items' in l:
            l['items'] = sort(l['items'])
    return sorted(data, key = lambda k: (-k['priority'] if 'priority' in k else 0, k['complete']))

def getItem(string, todoList):
    words = string.split(".")
    retList = []
    for w in words:
        index = int(w) - 1
        if not 'items' in todoList:
            break
        elif(index<0 or index>=len(todoList['items'])):
            print("No such todo")
            break
        todoList = todoList['items'][index]
        retList.append(index)
    return retList

def todoHandler(data):
    if "add" in data:
        data = data.replace("add", "", 1)
        if "comment" in data:
            data = data.replace("comment", "", 1)
            words = data.split()
            index = getItem(words[0], todoList)
            item = todoList
            for i in index:
                item = item['items'][i]
            item['comment'] = " ".join(words[1:])
        elif "due" in data or "due date" in data:
            data = data.replace("due date", "", 1)
            data = data.replace("due", "", 1)
            words = data.split()
            index = getItem(words[0], todoList)
            item = todoList
            for i in index:
                item = item['items'][i]
            removeReminder(item['uuid'].hex)
            item['due'] = parseDate(" ".join(words[1:]))
            addReminder(name=item['uuid'].hex, time=item['due'])
        else:
            data = " ".join(data.split())
            try:
                index = getItem(data.split()[0], todoList)
                item = todoList
                for i in index:
                    item = item['items'][i]
                data = " ".join(data.split()[1:])
            except ValueError:
                item = todoList
            newItem = {'complete':0, 'uuid':uuid.uuid4()}
            parts = data.split(" - ")
            newItem['name'] = parts[0]
            if " - " in data:
                newItem['comment'] = parts[1]
            if not 'items' in item:
                item['items'] = []
            item['items'].append(newItem)
    elif "remove" in data:
        data = data.replace("remove", "", 1)
        index = getItem(data.split()[0], todoList)
        deleteIndex = index.pop()
        item = todoList
        for i in index:
            item = item['items'][i]
        item['items'].remove(todoList['items'][deleteIndex])
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
        index = getItem(words[0], todoList)
        item = todoList
        for i in index:
            item = item['items'][i]
        item['priority'] = priority
    elif "complete" in data:
        data = data.replace("complete", "", 1)
        words = data.split()
        index = getItem(words[0], todoList)
        item = todoList
        for i in index:
            item = item['items'][i]
        complete = 100
        if words[1]:
            complete = int(words[1])
        item['complete'] = complete
    elif "help" in data:
        print(Fore.GREEN + "Commands: {add <todo description>, remove <index>, complete <index> [<completion>], priority <index> [<level>]}" + Fore.RESET)
        return

    todoList['items'] = sort(todoList['items'])
    _print(todoList['items'])
    writeFile("todolist.txt", todoList)

todoList = readFile("todolist.txt", {'items':[]})
todoList['items'] = sort(todoList['items'])

