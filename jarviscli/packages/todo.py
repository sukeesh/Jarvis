# -*- coding: utf-8 -*-

from datetime import datetime as dt
from uuid import uuid4
from .reminder import addReminder, removeReminder

from .fileHandler import write_file, read_file, str2date
from utilities.lexicalSimilarity import score_sentence
from utilities.textParser import parse_date, parse_number


from utilities.GeneralUtilities import error, info, critical, important, warning


def printItem(item, index):
    text = "<{2}> {0} [{1}%]".format(item['name'], item['complete'], index)
    if 'priority' in item and item['priority'] >= 100:
        critical(text)
    elif 'priority' in item and item['priority'] >= 50:
        important(text)
    else:
        print(text)
    if 'due' in item:
        text = "\tDue at {0}".format(item['due'].strftime("%Y-%m-%d %H:%M:%S"))
        if item['due'] < dt.now():
            critical(text)
        else:
            print(text)
    if item['comment']:
        print("\t{0}".format(item['comment']))


def _print(data, index=""):
    if len(data) == 0:
        info("ToDo list is empty, add a new entry with 'todo add <name>'")
    for x, element in enumerate(data):
        px = index + "{}".format(x + 1)
        printItem(element, px)
        if 'items' in element:
            _print(element['items'], px + ".")


def sort(data):
    for l in data:
        if 'items' in l:
            l['items'] = sort(l['items'])
    return sorted(data, key=lambda k: (-k['priority'] if 'priority' in k else 0, k['complete']))


def fixTypes(data):
    for l in data:
        if 'due' in l:
            l['due'] = str2date(l['due'])
            addReminder(name=l['name'], body=l['comment'],
                        uuid=l['uuid'], time=l['due'])
        if 'items' in l:
            l['items'] = fixTypes(l['items'])
    return data


def getItem(string, todoList):
    words = string.split(".")
    retList = []
    for w in words:
        index = int(w) - 1
        if 'items' not in todoList:
            break
        todoList = todoList['items'][index]
        retList.append(index)
    return retList


actions = {}


def addAction(function, trigger=[], minArgs=0):
    """
    Add a new action to the list of all available actions.

    :param function: Local function name that should be called when matched
    :param trigger: List of trigger words or sentences
    :param minArgs: Minimum number of arguments needed for given function
    """
    actions[function] = {'trigger': trigger, 'minArgs': minArgs}


def mixLists(a, b):
    """
    Concatenate every entry of both lists with eachother
    """
    ret = list()
    for x in a:
        for y in b:
            if x == "":
                ret.append(y)
            elif y == "":
                ret.append(x)
            else:
                ret.append(x + " " + y)
    return ret


addAction("handlerAdd", mixLists(
    ["add", "new", "create"], ["", "entry", "item"]), minArgs=1)


def handlerAdd(data):
    try:
        index = getItem(data.split()[0], todoList)
        item = todoList
        for i in index:
            item = item['items'][i]
        data = " ".join(data.split()[1:])
    except ValueError:
        item = todoList
    except IndexError:
        error("The Index for this item is out of range.")
        return
    newItem = {'complete': 0, 'uuid': uuid4().hex, 'comment': ""}
    parts = data.split(" - ")
    newItem['name'] = parts[0]
    if " - " in data:
        newItem['comment'] = parts[1]
    if 'items' not in item:
        item['items'] = []
    item['items'].append(newItem)
    write_file("todolist.txt", todoList)


addAction("handlerAddDue", ["add due", "due"], minArgs=2)


def handlerAddDue(data):
    words = data.split()
    try:
        index = getItem(words[0], todoList)
    except ValueError:
        error("The Index must be composed of numbers. Subitems are separated by a dot.")
        return
    except IndexError:
        error("The Index for this item is out of range.")
        return
    item = todoList
    for i in index:
        item = item['items'][i]
    removeReminder(item['uuid'])
    skip, item['due'] = parse_date(" ".join(words[1:]))
    urgency = 0
    if 'priority' in item:
        if item['priority'] >= 100:
            urgency = 2
        elif item['priority'] >= 50:
            urgency = 1
    addReminder(name=item['name'], body=item['comment'],
                uuid=item['uuid'], time=item['due'], urgency=urgency)
    write_file("todolist.txt", todoList)


addAction("handlerAddComment", ["add comment", "comment"], minArgs=2)


def handlerAddComment(data):
    words = data.split()
    try:
        index = getItem(words[0], todoList)
    except ValueError:
        error("The Index must be composed of numbers. Subitems are separated by a dot.")
        return
    except IndexError:
        error("The Index for this item is out of range.")
        return
    item = todoList
    for i in index:
        item = item['items'][i]
    item['comment'] = " ".join(words[1:])
    write_file("todolist.txt", todoList)


addAction("handlerRemove", mixLists(
    ["remove", "delete", "destroy"], ["", "entry", "item"]), minArgs=1)


def handlerRemove(data):
    try:
        index = getItem(data.split()[0], todoList)
        deleteIndex = index.pop()
    except ValueError:
        error("The Index must be composed of numbers. Subitems are separated by a dot.")
        return
    except IndexError:
        error("The Index for this item is out of range.")
        return
    item = todoList
    for i in index:
        item = item['items'][i]
    item['items'].remove(item['items'][deleteIndex])
    write_file("todolist.txt", todoList)


addAction("handlerPriority", ["priority"], minArgs=2)


def handlerPriority(data):
    words = data.split()
    names = ["normal", "high", "critical"]
    score = 100
    index = 0
    indexList = list()
    for i, key in enumerate(names):
        newScore, newList = score_sentence(data, key)
        if newScore < score:
            score = newScore
            index = i
            indexList = newList
    if score < 1:
        words.pop(indexList[0])
        priority = index * 50
    elif len(words) > 2:
        skip, priority = parse_number(" ".join(words[1:]))
    else:
        priority = 0
    try:
        index = getItem(words[0], todoList)
    except ValueError:
        error("The Index must be composed of numbers. Subitems are separated by a dot.")
        return
    except IndexError:
        error("The Index for this item is out of range.")
        return
    item = todoList
    for i in index:
        item = item['items'][i]
    item['priority'] = priority
    write_file("todolist.txt", todoList)


addAction("handlerComplete", ["complete", "finish"], minArgs=1)


def handlerComplete(data):
    words = data.split()
    try:
        index = getItem(words[0], todoList)
    except ValueError:
        error("The Index must be composed of numbers. Subitems are separated by a dot.")
        return
    except IndexError:
        error("The Index for this item is out of range.")
        return
    item = todoList
    for i in index:
        item = item['items'][i]
    complete = 100
    if len(words) > 1:
        try:
            complete = min(max(0, int(words[1])), 100)
        except ValueError:
            error("The completion level must be an integer between 0 and 100.")
            return
    item['complete'] = complete
    write_file("todolist.txt", todoList)


addAction("handlerList", ["list", "show", "print"])


def handlerList(data):
    todoList['items'] = sort(todoList['items'])
    _print(todoList['items'])


def todoHandler(data):
    """
    Handle the command string for todos.
    """
    indices = []
    score = 100
    action = 0
    minArgs = 0
    # Select the best trigger match from the actions list
    for key in actions:
        foundMatch = False
        for trigger in actions[key]['trigger']:
            newScore, indexList = score_sentence(data, trigger, distance_penalty=0.5, additional_target_penalty=0,
                                                 word_match_penalty=0.5)
            if foundMatch and len(indexList) > len(indices):
                # A match for this action was already found.
                # But this trigger matches more words.
                indices = indexList
            if newScore < score:
                if not foundMatch:
                    indices = indexList
                    minArgs = actions[key]['minArgs']
                    foundMatch = True
                score = newScore
                action = key
    if not action:
        return
    data = data.split()
    for i in sorted(indices, reverse=True):
        del data[i]
    if len(data) < minArgs:
        warning(
            "Not enough arguments for specified command {0}".format(action))
        return
    data = " ".join(data)
    globals()[action](data)


todoList = read_file("todolist.txt", {'items': []})
todoList['items'] = fixTypes(sort(todoList['items']))
