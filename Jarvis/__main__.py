# -*- coding: utf-8 -*-
import os, sys, json
from time import ctime
from pprint import pprint

import pyowm, requests
from colorama import init
from colorama import Fore, Back, Style

import todo, newws, mapps, picshow, evaluator, audioHandler

#reload(sys)
#sys.setdefaultencoding('utf-8')

isSpeech = 0

def go(data):
    if isSpeech:
        audioHandler.speak(data)
    else:
        print(data)

def Jarvis(data):
    data = str.lower(data)
    if "how are you" in data:
        go(Fore.BLUE + "I am fine, How about you" + Fore.RESET)

    if "what time is it" in data:
        go(Fore.BLUE + ctime() + Fore.RESET)

    if "open camera" in data:
        go("Opening Cheese ...... ")
        os.system("cheese")

    if "where am i" in data:
        mapps.locateme()

    if "weather" in data:
        mapps.weatherr()

    if "near me" in data:
        mapps.nearme(data)

    if "movies" in data:
        try:
            movie_name = raw_input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)
        except:
            movie_name = input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)

        os.system("ims " + movie_name)

    if "music" in data:
        os.system("instantmusic")

    if "increase volume" in data:
        os.system("pactl -- set-sink-volume 0 +3%")

    if "decrease volume" in data:
        os.system("pactl -- set-sink-volume 0 -10%")

    if "hotspot start" in data:
        os.system("sudo ap-hotspot start")

    if "hotspot stop" in data:
        os.system("sudo ap-hotspot stop")

    if "search for a string in file" in data:
        try:
            file_name = raw_input(Fore.RED + "Enter file name?:\n" + Fore.RESET)
            stringg = raw_input(Fore.GREEN + "Enter string:\n" + Fore.RESET)
        except:
            file_name = input(Fore.RED + "Enter file name?:\n" + Fore.RESET)
            stringg = input(Fore.GREEN + "Enter string:\n" + Fore.RESET)

        os.system("grep '" + stringg + "' " + file_name)

    if "check ram" in data:
        os.system("free -lm")

    if "todo" in data:
        todo.todoHandler(data)

    if "news" in data:
        newws.show_news()

    if "show me pics of" in data:
        picshow.showpics(data)

    if "evaluate" in data:
        tempt = data.split(" ", 1) or ""
        if len(tempt) > 1:
            evaluator.calc(tempt[1])
        else:
            print(Fore.RED + "Error : Not in correct format" + Fore.RESET)

    if "show me directions from" in data:
        mapps.directions(data)
	
    if "quit" in data or "exit" in data or "goodbye" in data:
        print(Fore.RED + "Goodbye, see you later!" + Fore.RESET)
        exit();

while 1:
    if isSpeech:
        speak(Fore.RED + "Hi, What can I do for you?" + Fore.RESET)
        some = audioHandler.recordAudio()
        Jarvis(some)
    else:
        print(Fore.RED + "Hi, What can I do for you?" + Fore.RESET)
        try:
            some = raw_input()
        except:
            some = input()
        Jarvis(some)

