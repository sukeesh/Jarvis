# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime as dt
from uuid import uuid4
from reminder import addReminder, removeReminder
from colorama import Fore, Back

from fileHandler import writeFile, readFile, str2date
from utilities.lexicalSimilarity import scoreSentence
from utilities.textParser import parseDate, parseNumber

def printItem(item, index):
    if 'priority' in item and item['priority'] >= 50:
        sys.stdout.write(Fore.YELLOW)
    if 'priority' in item and item['priority'] >= 100:
        sys.stdout.write(Fore.RED)
    print("<{2}> {0} [{1}%]".format(item['name'], item['complete'], index) + Fore.RESET)
    if 'due' in item:
        if item['due'] < dt.now():
            sys.stdout.write(Fore.RED)
        print("\tDue at {0}".format(item['due'].strftime("%Y-%m-%d %H:%M:%S")) + Fore.RESET)
    if item['comment']:
        print("\t{0}".format(item['comment']))

def _print(data, index = ""):
    if len(data) == 0:
        print("ToDo list is empty, add a new entry with 'todo add <name>'")
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

def fixTypes(data):
    for l in data:
        if 'due' in l:
            l['due'] = str2date(l['due'])
            addReminder(name=l['name'], body=l['comment'], uuid=l['uuid'], time=l['due'])
        if 'items' in l:
            l['items'] = fixTypes(l['items'])
    return data

def getItem(string, todoList):
    words = string.split(".")
    retList = []
    for w in words:
        index = int(w) - 1
        if not 'items' in todoList:
            break
        todoList = todoList['items'][index]
        retList.append(index)
    return retList

actions = { "handlerAdd": ["add", "new"],
            "handlerAddDue": ["add due", "due"],
            "handlerAddComment": ["add comment", "comment"],
            "handlerRemove": ["remove", "delete"],
            "handlerPriority" : ["priority"],
            "handlerComplete": ["complete"],
            "handlerList": ["list", "show", "print"]}
def reactions(key, data):
    def handlerAdd(data):
        if not numWords:
            print(Fore.RED + "Not enough arguments for 'todo add <title>'" + Fore.RESET)
            return
        data = " ".join(data.split())
        try:
            index = getItem(data.split()[0], todoList)
            item = todoList
            for i in index:
                item = item['items'][i]
            data = " ".join(data.split()[1:])
        except ValueError:
            item = todoList
        except IndexError:
            print(Fore.RED + "The Index for this item is out of range." + Fore.RESET)
            return
        newItem = {'complete':0, 'uuid':uuid4().hex, 'comment':""}
        parts = data.split(" - ")
        newItem['name'] = parts[0]
        if " - " in data:
            newItem['comment'] = parts[1]
        if not 'items' in item:
            item['items'] = []
        item['items'].append(newItem)
        writeFile("todolist.txt", todoList)

    def handlerAddComment(data):
        if numWords < 2:
            print(Fore.RED + "Not enough arguments for 'todo add comment <index> <comment>'" + Fore.RESET)
            return
        words = data.split()
        try:
            index = getItem(words[0], todoList)
        except ValueError:
            print(Fore.RED + "The Index must be composed of numbers. Subitems are separated by a dot." + Fore.RESET)
            return
        except IndexError:
            print(Fore.RED + "The Index for this item is out of range." + Fore.RESET)
            return
        item = todoList
        for i in index:
            item = item['items'][i]
        item['comment'] = " ".join(words[1:])
        writeFile("todolist.txt", todoList)

    def handlerAddDue(data):
        if numWords < 2:
            print(Fore.RED + "Not enough arguments for 'todo add due <index> <time>'" + Fore.RESET)
            return
        words = data.split()
        try:
            index = getItem(words[0], todoList)
        except ValueError:
            print(Fore.RED + "The Index must be composed of numbers. Subitems are separated by a dot." + Fore.RESET)
            return
        except IndexError:
            print(Fore.RED + "The Index for this item is out of range." + Fore.RESET)
            return
        item = todoList
        for i in index:
            item = item['items'][i]
        removeReminder(item['uuid'])
        skip, item['due'] = parseDate(" ".join(words[1:]))
        urgency = 0
        if 'priority' in item:
            if item['priority'] >= 100:
                urgency = 2
            elif item['priority'] >= 50:
                urgency = 1
        addReminder(name=item['name'], body=item['comment'], uuid=item['uuid'], time=item['due'], urgency=urgency)
        writeFile("todolist.txt", todoList)

    def handlerRemove(data):
        if not numWords == 1:
            return
        try:
            index = getItem(data.split()[0], todoList)
            deleteIndex = index.pop()
        except ValueError:
            print(Fore.RED + "The Index must be composed of numbers. Subitems are separated by a dot." + Fore.RESET)
            return
        except IndexError:
            print(Fore.RED + "The Index for this item is out of range." + Fore.RESET)
            return
        item = todoList
        for i in index:
            item = item['items'][i]
        item['items'].remove(item['items'][deleteIndex])
        writeFile("todolist.txt", todoList)

    def handlerPriority(data):
        if not numWords >= 2:
            return
        words = data.split()
        #TODO move to lexical similarity
        if "critical" in data:
            data = data.replace("critical", "", 1)
            priority = 100
        elif "high" in data:
            data = data.replace("high", "", 1)
            priority = 50
        elif "normal" in data:
            data = data.replace("normal", "", 1)
            priority = 0
        elif numWords > 2:
            skip, priority = parseNumber(" ".join(words[1:]))
        else:
            priority = 0
        words = data.split()
        try:
            index = getItem(words[0], todoList)
        except ValueError:
            print(Fore.RED + "The Index must be composed of numbers. Subitems are separated by a dot." + Fore.RESET)
            return
        except IndexError:
            print(Fore.RED + "The Index for this item is out of range." + Fore.RESET)
            return
        item = todoList
        for i in index:
            item = item['items'][i]
        item['priority'] = priority
        writeFile("todolist.txt", todoList)

    def handlerComplete(data):
        if not numWords >= 1:
            return
        words = data.split()
        try:
            index = getItem(words[0], todoList)
        except ValueError:
            print(Fore.RED + "The Index must be composed of numbers. Subitems are separated by a dot." + Fore.RESET)
            return
        except IndexError:
            print(Fore.RED + "The Index for this item is out of range." + Fore.RESET)
            return
        item = todoList
        for i in index:
            item = item['items'][i]
        complete = 100
        if len(words) > 1:
            try:
                complete = min(max(0, int(words[1])), 100)
            except ValueError:
                print(Fore.RED + "The completion level must be an integer between 0 and 100." + Fore.RESET)
                return
        item['complete'] = complete
        writeFile("todolist.txt", todoList)

    def handlerList(data):
        todoList['items'] = sort(todoList['items'])
        _print(todoList['items'])

    numWords = len(data.split())
    locals()[key](data)

def todoHandler(data):
    indices = []
    score = 100
    action = 0
    for key in actions:
        foundMatch = False
        for trigger in actions[key]:
            newScore, indexList = scoreSentence(data, trigger, distancePenalty = 0.5, additionalTargetPenalty = 0, wordMatchPenalty = 0.5)
            print trigger
            print newScore
            print indexList
            if foundMatch and len(indexList) > len(indices):
                indices = indexList
            if newScore < score:
                if not foundMatch:
                    indices = indexList
                    foundMatch = True
                score = newScore
                action = key
    if not action:
        return
    data = data.split();
    for i in sorted(indices, reverse=True):
        del data[i]
    data = " ".join(data)
    print data
    print action
    reactions(action, data)

todoList = readFile("todolist.txt", {'items':[]})
todoList['items'] = fixTypes(sort(todoList['items']))

