# -*- coding: utf-8 -*-

import os
import json

from datetime import datetime as dt
from datetime import date, time, timedelta
from uuid import uuid4
from threading import Timer
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

from colorama import init
from colorama import Fore, Back, Style

from fileHandler import writeFile, readFile, str2date
from utilities.lexicalSimilarity import findTrigger, compareSentence
from utilities.textParser import parseNumber, parseDate

def sort(data):
    return sorted(data, key = lambda k: (k['time']))

def findReminder(string):
    """
    Find reminder by name.

    Search for the given name in the reminderList. A match is determined by similarity
    between request and the available reminder names.
    """
    nameList = [k['name'] for k in reminderList['items']]
    if not len(nameList):
        return (-1, [])
    index, score, indexList = compareSentence(nameList, string)
    if score < 1.0 and not reminderList['items'][index]['hidden']:
        return (index, indexList)
    return (-1, [])

def showAlarm(notification, name):
    print(Fore.BLUE + name + Fore.RESET)
    notification.show()

def showNotification(name, body):
    """
    Show a notification immediately.
    """
    Notify.Notification.new(name, body).show()

def addReminder(name, time, uuid, body = '', urgency=Notify.Urgency.LOW, hidden = True):
    """
    Queue reminder.

    Show notification at the specified time. With the given name as title and an optional body
    for further information.
    The mandatory is used to identify the reminder and remove it with removeReminder().
    If the reminder should show up in the list printed by 'remind print' hidden (default: True)
    should be set to false. In this case the reminder is requeued at startup. If reminders are
    used e.g. with a todo list for due dates, hidden should probably be set to true so that the
    list is not cluttered with automatically created data.
    If the reminder needs a different priority, it can be set with urgency to critical (=2),
    high (=1) or normal (=0, default).
    """
    waitTime = time - dt.now()
    n = Notify.Notification.new(name, body)
    n.set_urgency(urgency)
    timerList[uuid] = Timer(waitTime.total_seconds(), showAlarm, [n, name])
    timerList[uuid].start()
    newItem = {'name':name, 'time':time, 'hidden':hidden, 'uuid':uuid}
    reminderList['items'].append(newItem)
    reminderList['items'] = sort(reminderList['items'])
    writeFile("reminderlist.txt", reminderList)

def removeReminder(uuid):
    """
    Remove and cancel previously added reminder identified by the given uuid.
    """
    if uuid in timerList:
        timerList[uuid].cancel()
        timerList.pop(uuid)
    for index, e in enumerate(reminderList['items']):
        if uuid == e['uuid']:
            reminderList['items'].remove(reminderList['items'][index])
            break;
    writeFile("reminderlist.txt", reminderList)

actions = { "add": "handlerAdd",
            "remove": "handlerRemove",
            "delete": "handlerRemove",
            "list": "handlerList",
            "print": "handlerList",
            "clear": "handlerClear"}
def reactions(key, data):
    def handlerAdd(data):
        skip, time = parseDate(data)
        if skip:
            addReminder(name=" ".join(data.split()[skip:]), time=time, hidden=False, uuid=uuid4().hex)

    def handlerRemove(data):
        skip, number = parseNumber(data)
        if skip:
            index = number - 1
        else:
            index, indexList = findReminder(data)
        if index >= 0 and index < len(reminderList['items']):
            print("Removed reminder: \"{0}\"".format(reminderList['items'][index]['name']))
            removeReminder(reminderList['items'][index]['uuid'])
        else:
            print("Could not find selected reminder")

    def handlerList(data):
        count = 0
        for index, e in enumerate(reminderList['items']):
            if not e['hidden']:
                print("<{0}> {2}: {1}".format(index + 1, e['time'], e['name']))
                count += 1
        if count == 0:
            print("Reminder list is empty, add a new entry with 'remind add <time> <name>'")

    def handlerClear(data):
        reminderList['items'] = [k for k in reminderList['items'] if k['hidden']]
        writeFile("reminderlist.txt", reminderList)

    locals()[key](data)

def reminderHandler(data):
    index = 100
    action = 0
    for key in actions:
        newIndex = findTrigger(data, key)
        if not newIndex == -1:
            if newIndex < index:
                index = newIndex
                action = actions[key]
    if not action:
        return
    data = data.split();
    data.pop(index)
    data = " ".join(data)
    reactions(action, data)

def reminderQuit():
    """
    This function has to be called when shutting down. It terminates all waiting threads.
    """
    for index, el in timerList.iteritems():
        el.cancel()

timerList = {}
reminderList = readFile("reminderlist.txt", {'items':[]})
reminderList['items'] = sort(reminderList['items'])
reminderList['items'] = [i for i in reminderList['items'] if not i['hidden']]
for e in reminderList['items']:
    e['time'] = str2date(e['time'])
    waitTime = e['time'] - dt.now()
    n = Notify.Notification.new(e['name'])
    n.set_urgency(Notify.Urgency.LOW)
    timerList[e['uuid']] = Timer(waitTime.total_seconds(), showAlarm, [n, e['name']])
    timerList[e['uuid']].start()

Notify.init("Jarvis")

