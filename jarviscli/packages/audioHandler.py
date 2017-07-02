# -*- coding: utf-8 -*-
import os

from gtts import gTTS
import speech_recognition as sr


def record_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    data = None
    try:
        data = str(r.recognize_google(audio))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(
            "Could not request results from Google Speech Recognition service; {0}".format(e))
    return data or ""


def speak(audio_string):
    print(audio_string)
    tts = gTTS(text=audio_string, lang='en')
    tts.save("here.mp3")
    os.system("mpg123 here.mp3")
