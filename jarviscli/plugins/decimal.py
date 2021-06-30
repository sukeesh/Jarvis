from plugin import plugin

from colorama import Fore


@plugin("revert_binary")
def rev_binary(jarvis, s):
    """
    Convert Binary number in Decimal Base
    """
    if s == "":
        s = jarvis.input("What's your number in binary ? ")
        cpt = 0
        for i in range(len(s)):
            if s[-1 - i] == "1" or s[-1 - i] == "0":
                cpt += (int(s[-1 - i])) * 2 ** i
            else:
                jarvis.say("It's not a number in binary")
                return
        jarvis.say(str(cpt), Fore.GREEN)


@plugin("revert_hex")
def rev_hex(jarvis, s):
    """
    Convert Hexadecimal number in Decimal Base
    """
    dict_hex = {
        "0": 0,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "A": 10,
        "B": 11,
        "C": 12,
        "D": 13,
        "E": 14,
        "F": 15
    }
    if s == "":
        s = jarvis.input("What's your number in hexadecimal ? ")
        cpt = 0
        for i in range(len(s)):
            if s[-1 - i].upper() in dict_hex.keys():
                cpt += (dict_hex[s[-1 - i].upper()]) * 16 ** i
            else:
                jarvis.say("It's not a number in hexadecimal")
                return
        jarvis.say(str(cpt), Fore.GREEN)


@plugin("convert_base")
def convert_base(jarvis, s):
    global firstbase, number, secondbase, index
    if s == "":
        firstbase = jarvis.input("What's your base ? ")
        number = jarvis.input("What's your number ? ")
        secondbase = jarvis.input("Which base do you want for you number ? ")
    else:
        if len(s.split(" ")) > 3:
            index = 1
            lst = s.split()
            for k in lst:
                try :
                    test=int(k)
                    if index==1 :
                        firstbase =test
                        index +=1
                    else:
                        secondbase =test
                except ValueError :
                    pass
            if index !=2 :
                jarvis.say("Give two bases to start")
                return
            number = jarvis.input("What's your number ? ")
        else:
            lst = s.split(" ")
            firstbase, number, secondbase = lst[0], lst[1], lst[2]
    firstbase = int(firstbase)
    secondbase = int(secondbase)
    deciNumber = toDeci(number, firstbase)
    if deciNumber == -1:
        jarvis.say("Your input is invalid ")
        return
    jarvis.say(str(fromDeci(secondbase, deciNumber)))


def val(c):
    if '0' <= c <= '9':
        return ord(c) - ord('0')
    else:
        return ord(c) - ord('A') + 10


def toDeci(number, base):
    """
    inspired by geeksforgeeks.org/convert-base-decimal-vice-versa/
    """
    n = len(number)
    power = 1
    num = 0
    for i in range(n - 1, -1, -1):
        if val(number[i]) >= base:
            return -1
        num += val(number[i]) * power
        power = power * base
    return num


def val1(c):
    if 0 <= c <= 9:
        return chr(c + ord('0'))
    else:
        return chr(c - 10 + ord('A'))


def fromDeci(base, inputNumber):
    result = ""
    while inputNumber > 0:
        result += val1(inputNumber % base)
        inputNumber = inputNumber // base
    return result[::-1]
