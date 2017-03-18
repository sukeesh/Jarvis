# -*- coding: utf-8 -*-
import os
import sys
import json

from colorama import init
from colorama import Fore, Back, Style

todoList = {}
todoList['items'] = []

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
    print(Fore.RED + "Commands Avaliable {add <todo description>, remove <index>, complete <index> [<completion>]}" + Fore.RESET)

def sort(data):
    return sorted(data, key = lambda k: (-k['priority'] if 'priority' in k else 0, k['complete']))
    
def todoHandler(data):
    global todoList
    with open("todolist.txt", "r+") as f:
        todoList = json.load(f)
        sort(todoList['items'])
    _print(todoList['items'])

    while 1:
        try:
            inp = raw_input()
        except:
            inp = input()
        temp = inp.split()
        c = temp[0]
        s = temp[1] if len(temp) > 1 else "0"
        arg = temp[2] if len(temp) > 2 else 0
        if(c == "add"):
            todoList['items'].append({'name':s, 'complete':0})
        elif(c == "remove"):
            index = int(s)
            if(index<0 or index>=len(todoList['items'])):
                print("No such todo")
                continue
            todoList['items'].remove(todoList['items'][index])

        elif(c == "complete"):
            index = int(s)
            if(index<0 or index>=len(todoList['items'])):
                print("No such todo")
                continue
            complete = 100
            if arg:
                complete = int(arg)
            todoList['items'][index]['complete'] = complete
        elif(c == "priority"):
            index = int(s)
            if(index<0 or index>=len(todoList['items'])):
                print("No such todo")
                continue
            todoList['items'][index]['priority'] = int(arg)
        elif(c == "exit" or c == "quit"):
            break;
        else:
            print("No such command")
            continue;
        sort(todoList['items'])
        print("Update list =>")
        _print(todoList['items'])
        writeToFile()

if not os.path.exists("todolist.txt"):
    writeToFile()
