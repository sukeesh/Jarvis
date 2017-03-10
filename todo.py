import os
from colorama import init
from colorama import Fore, Back, Style

def writeToFile(l1,l2):
    f = open("todolist.txt", "w+")
    for l in l1:
        f.write("%s@@@@1\n"%(l))

    for l in l2:
        f.write("%s@@@@0\n" % (l))


def _print(l1,l2):
    print("Pending => ")
    x = 0
    for l in l1:
        print("[%d] %s"%((x,l)))
        x += 1
    print("Completed => ")
    for l in l2:
        print("[%d] %s" % ((x, l)))
        x += 1
    print(Fore.RED +"Commands Avaliable {add <todo>, remove <index>, move<index>}"+Fore.RESET)

def todoHandler(data):
    f = open("todolist.txt", "r+")
    lines = f.readlines()
    f.close()
    completed_list = []
    notcompleted_list = []
    for l in lines:
        x,y = l.split("@@@@")
        if(y[0]=='1'):completed_list.append(x)
        else : notcompleted_list.append(x)
    _print(completed_list,notcompleted_list)

    while 1:
        inp = raw_input()
        temp = inp.split(" ",1)
        c = temp[0]
        s = "0"
        if(len(temp)>1):s = temp[1]
        if(c=="add"):
            completed_list.append(s)
        elif(c=="remove"):
            x = int(s)
            if(x<0 or x>=len(completed_list)+len(notcompleted_list)):
                print("no such todo")
                continue
            if(x<len(completed_list)):
                completed_list.remove(completed_list[x])
            else:
                x -= len(completed_list)
                notcompleted_list.remove(notcompleted_list[x])

        elif(c=="move"):
            x = int(s)
            if(x<0 or x>=len(completed_list)+len(notcompleted_list)):
                print("no such todo")
                continue
            if(x<len(completed_list)):
                p = completed_list[x]
                completed_list.remove(p)
                notcompleted_list.append(p)
            else:
                x -= len(completed_list)
                p = notcompleted_list[x]
                notcompleted_list.remove(p)
                completed_list.append(p)
        elif(c=="exit"):
            break;
        else:
            print("No such command")
            continue;
        print("Update list =>")
        _print(completed_list,notcompleted_list)
        writeToFile(completed_list,notcompleted_list)

os.system("touch todolist.txt")