import os

from colorama import init
from colorama import Fore, Back, Style

def writeToFile(l1,l2):
    with open("todolist.txt", "w+") as f:
        for l in l1:
            f.write("{}@@@@1\n".format(l))

        for l in l2:
            f.write("{}@@@@0\n".format(l))


def _print(l1,l2):
    print("Pending => ")
    x = 0
    for l in l1:
        print("[{0}] {1}".format(x, l))
        x += 1
    print("Completed => ")
    for l in l2:
        print("[{0}] {1}".format(x, l))
        x += 1
    print(Fore.RED +"Commands Avaliable {add <todo>, remove <index>, move<index>}"+Fore.RESET)

def todoHandler(data):
    with open("todolist.txt", "r+") as f:
        lines = f.readlines()
    completed_list = []
    notcompleted_list = []
    for l in lines:
        x,y = l.split("@@@@")
        if(y[0]=='1'): completed_list.append(x)
        else : notcompleted_list.append(x)
    _print(completed_list,notcompleted_list)

    while 1:
        try:
            inp = raw_input()
        except:
            inp = input()
        temp = inp.split(" ", 1)
        c = temp[0]
        s = temp[1] if len(temp) > 1 else "0"
        if(c == "add"):
            completed_list.append(s)
        elif(c == "remove"):
            x = int(s)
            if(x<0 or x>=len(completed_list)+len(notcompleted_list)):
                print("no such todo")
                continue
            if(x < len(completed_list)):
                completed_list.remove(completed_list[x])
            else:
                x -= len(completed_list)
                notcompleted_list.remove(notcompleted_list[x])

        elif(c == "move"):
            x = int(s)
            if(x<0 or x>=len(completed_list)+len(notcompleted_list)):
                print("no such todo")
                continue
            if(x < len(completed_list)):
                p = completed_list[x]
                completed_list.remove(p)
                notcompleted_list.append(p)
            else:
                x -= len(completed_list)
                p = notcompleted_list[x]
                notcompleted_list.remove(p)
                completed_list.append(p)
        elif(c == "exit"):
            break;
        else:
            print("No such command")
            continue;
        print("Update list =>")
        _print(completed_list,notcompleted_list)
        writeToFile(completed_list,notcompleted_list)


if not os.path.exists("todolist.txt"):
    with open("todolist.txt", 'w'):
        pass
