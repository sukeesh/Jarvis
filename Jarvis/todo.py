# -*- coding: utf-8 -*-
import os
import sys
import json

from colorama import init
from colorama import Fore, Back, Style

def writeToFile():
    with open("todolist.txt", "w+") as f:
        json.dump(todoList, f)

def _print(data):
    x = 0
    for l in data:
        if 'priority' in l and l['priority'] >= 50:
            sys.stdout.write(Fore.YELLOW)
        if 'priority' in l and l['priority'] >= 100:
            sys.stdout.write(Fore.RED)
        print("<{2}> {0} [{1}%]".format(l['name'], l['complete'], x) + Fore.RESET)
        x += 1

def sort(data):
    return sorted(data, key = lambda k: (-k['priority'] if 'priority' in k else 0, k['complete']))
    
def todoHandler(data):
    global todoList
    words = data.split()
    s = words[1] if len(words) > 1 else "0"
    arg = words[2] if len(words) > 2 else 0
    if "add" in data:
        name = " ".join(words[1:])
        todoList['items'].append({'name':name, 'complete':0})
    elif "remove" in data:
        index = int(s)
        if(index<0 or index>=len(todoList['items'])):
            print("No such todo")
            return
        todoList['items'].remove(todoList['items'][index])
    elif "priority" in data:
        index = int(s)
        if(index<0 or index>=len(todoList['items'])):
            print("No such todo")
            return
        todoList['items'][index]['priority'] = int(arg)
    elif "complete" in data:
        index = int(s)
        if(index<0 or index>=len(todoList['items'])):
            print("No such todo")
            return
        complete = 100
        if arg:
            complete = int(arg)
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

