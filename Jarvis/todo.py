# -*- coding: utf-8 -*-
import os
import json

from colorama import init
from colorama import Fore, Back, Style

todoList = {}
todoList['items'] = []

def writeToFile():
    with open("todolist.txt", "w+") as f:
        json.dump(todoList, f)

def _print(list):
    x = 0
    for l in list:
        print("<{2}> {0} [{1}%]".format(l['name'], l['complete'], x))
        x += 1
    print(Fore.RED +"Commands Avaliable {add <todo description>, remove <index>, complete <index>}"+Fore.RESET)

def todoHandler(data):
    global todoList
    with open("todolist.txt", "r+") as f:
        todoList = json.load(f)
    _print(todoList['items'])

    while 1:
        try:
            inp = raw_input()
        except:
            inp = input()
        temp = inp.split(" ", 1)
        c = temp[0]
        s = temp[1] if len(temp) > 1 else "0"
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
            todoList['items'][index]['complete'] = 100;
        elif(c == "exit" or c == "quit"):
            break;
        else:
            print("No such command")
            continue;
        print("Update list =>")
        _print(todoList['items'])
        writeToFile()

if not os.path.exists("todolist.txt"):
    with open("todolist.txt", 'w') as f:
        json.dump(todoList, f)
