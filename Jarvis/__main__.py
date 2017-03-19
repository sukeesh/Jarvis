# -*- coding: utf-8 -*-
from os import system
from time import ctime
from colorama import Fore
from packages.audioHandler import speak
from packages import todo, newws, mapps, picshow, evaluator, audioHandler, music
import Jarvis

global isSpeech
isSpeech = 0

def go(data):
    if isSpeech:
        audioHandler.speak(data)
    else:
        print(data)

def main():
    flag = True
    while flag:
        if isSpeech:
            """
            speak(Fore.RED + "Hi, What can I do for you?" + Fore.RESET)
            some = audioHandler.recordAudio()
            Jarvis(some)
            """
        else:
            jarvis = Jarvis.Jarvis()
            jarvis.executor()

if __name__ == '__main__':
    main()
