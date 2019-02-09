#!/usr/bin/env python3
import speech_recognition as sr
import pyttsx3
import os
from plugin import plugin
@plugin()
def hear(jarvis, s):
    r = sr.Recognizer()
    engine = pyttsx3.init()
    listen = False

    while listen is False:
        try:
            with sr.Microphone() as source:
                os.system('reset')
                print("Say listen to start listening")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                pinger = r.recognize_google(audio)
            try:
                if (pinger.lower() == "listen"):
                    listen = True
                    print("Voice mode activated. Say something!")
                    break
                else:
                    continue
            except LookupError:
                continue
        except sr.UnknownValueError:
            continue

    while listen is True:
        print("Say somthing")
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                pinger = r.recognize_google(audio).lower()

            if (pinger == "stop"):
                listen = False
                print("Listening stopped.")
                break
            else:
                print(pinger)
                if listen:
                    line = pinger
                    _jarvis = jarvis._jarvis
                    line = _jarvis.precmd(line)
                    stop = _jarvis.onecmd(line)
                    stop = _jarvis.postcmd(stop, line)

        except LookupError:
            engine.say('Audio cannot be read!')
            engine.runAndWait()
            print("Could not understand audio")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            continue
        except sr.RequestError:
            print("Could not request results from Google Recognition service")
            continue
