# -*- coding: utf-8 -*-

from datetime import datetime as dt
from uuid import uuid4
from threading import Timer


from .fileHandler import write_file, read_file, str2date
from utilities.lexicalSimilarity import score_sentence, compare_sentence
from utilities.textParser import parse_number, parse_date
from utilities.GeneralUtilities import (
    error, info, MACOS, IS_MACOS, unsupported
)

if not IS_MACOS:
    import notify2


def sort(data):
    """
    Sort list of reminders by time (oldest first).
    """
    return sorted(data, key=lambda k: (k['time']))


def find_reminder(string):
    """
    Find reminder by name.

    Search for the given name in the reminderList. A match is determined by similarity
    between request and the available reminder names.
    """
    nameList = [k['name'] for k in reminderList['items']]
    if not len(nameList):
        return (-1, [])
    index, score, indexList = compare_sentence(nameList, string)
    if score < 1.0 and not reminderList['items'][index]['hidden']:
        return (index, indexList)
    return (-1, [])


def showAlarm(notification, name):
    info(name)
    notification.show()


def showNotification(name, body):
    """
    Show a notification immediately.
    """
    notify2.Notification(name, body).show()


def addReminder(name, time, uuid, body='', urgency=0, hidden=True):
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
    n = notify2.Notification(name, body)
    n.set_urgency(urgency)
    timerList[uuid] = Timer(waitTime.total_seconds(), showAlarm, [n, name])
    timerList[uuid].start()
    newItem = {'name': name, 'time': time, 'hidden': hidden, 'uuid': uuid}
    reminderList['items'].append(newItem)
    reminderList['items'] = sort(reminderList['items'])
    write_file("reminderlist.txt", reminderList)


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
            break
    write_file("reminderlist.txt", reminderList)


actions = {}


def addAction(function, trigger=[], minArgs=0):
    """
    Add a new action to the list of all available actions.

    :param function: Local function name that should be called when matched
    :param trigger: List of trigger words or sentences
    :param minArgs: Minimum number of arguments needed for given function
    """
    actions[function] = {'trigger': trigger, 'minArgs': minArgs}


addAction("handlerAdd", ["add", "new", "create"], minArgs=1)


def handler_add(data):
    skip, time = parse_date(data)
    if skip:
        addReminder(
            name=" ".join(data.split()[skip:]), time=time, hidden=False, uuid=uuid4().hex)


addAction("handlerRemove", ["remove", "delete", "destroy"], minArgs=1)


def handler_remove(data):
    skip, number = parse_number(data)
    if skip:
        index = number - 1
    else:
        index, index_list = find_reminder(data)
    if 0 <= index < len(reminderList['items']):
        info("Removed reminder: \"{0}\"".format(
            reminderList['items'][index]['name']))
        removeReminder(reminderList['items'][index]['uuid'])
    else:
        error("Could not find selected reminder")


addAction("handlerList", ["list", "print", "show"])


def handler_list(data):
    count = 0
    for index, en in enumerate(reminderList['items']):
        if not en['hidden']:
            print("<{0}> {2}: {1}".format(count + 1, en['time'], en['name']))
            count += 1
    if count == 0:
        info("Reminder list is empty. Add a new entry with 'remind add <time> <name>'")


addAction("handlerClear", ["clear"])


def handler_clear(data):
    reminderList['items'] = [k for k in reminderList['items'] if k['hidden']]
    write_file("reminderlist.txt", reminderList)


@unsupported(platform=MACOS)
def reminder_handler(data):
    """
    Handle the command string for reminders.
    """
    indices = []
    score = 100
    action = 0
    min_args = 0
    # Select the best trigger match from the actions list
    for key in actions:
        found_match = False
        for trigger in actions[key]['trigger']:
            new_score, index_list = score_sentence(data, trigger, distance_penalty=0.5, additional_target_penalty=0,
                                                   word_match_penalty=0.5)
            if found_match and len(index_list) > len(indices):
                # A match for this action was already found.
                # But this trigger matches more words.
                indices = index_list
            if new_score < score:
                if not found_match:
                    indices = index_list
                    min_args = actions[key]['minArgs']
                    found_match = True
                score = new_score
                action = key
    if not action:
        return
    data = data.split()
    for j in sorted(indices, reverse=True):
        del data[j]
    if len(data) < min_args:
        error("Not enough arguments for specified command {0}".format(action))
        return
    data = " ".join(data)
    globals()[action](data)


@unsupported(platform=MACOS, silent=True)
def reminder_quit():
    """
    This function has to be called when shutting down. It terminates all waiting threads.
    """
    try:
        for index, el in timerList.iteritems():
            el.cancel()
    except:
        for index, el in timerList.items():
            el.cancel()


if not IS_MACOS:
    timerList = {}
    reminderList = read_file("reminderlist.txt", {'items': []})
    reminderList['items'] = sort(reminderList['items'])
    reminderList['items'] = [
        i for i in reminderList['items'] if not i['hidden']]
    notify2.init("Jarvis")
    for e in reminderList['items']:
        e['time'] = str2date(e['time'])
        waitTime = e['time'] - dt.now()
        n = notify2.Notification(e['name'])
        n.set_urgency(0)
        timerList[e['uuid']] = Timer(
            waitTime.total_seconds(), showAlarm, [n, e['name']])
        timerList[e['uuid']].start()
