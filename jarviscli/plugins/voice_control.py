import os
from plugin import plugin, require

voice_control_installed = True
try:
    import speech_recognition as sr
    import pyaudio
except ImportError:
    voice_control_installed = False

if voice_control_installed:
    requirements = []
else:
    requirements = [
        'voice_control_requirements (install portaudio + re-run setup.sh)']


@require(native=requirements)
@plugin("hear")
def hear(jarvis, s):
    r = sr.Recognizer()  # intializing the speech_recognition
    listen = False
    _jarvis = jarvis._jarvis  # calling jarvis object.
    _jarvis.speech.text_to_speech("Say listen to start voice mode")
    while listen is False:
        try:
            with sr.Microphone() as source:
                os.system('reset')  # for clearing the terminal.
                print("Say listen to start listening")
                r.adjust_for_ambient_noise(source)  # Eleminating the noise.
                audio = r.listen(source)  # Storing audio.
                pinger = r.recognize_google(audio)  # Converting speech to text
            try:
                if (pinger.lower() == "listen"):
                    listen = True
                    _jarvis.speech.text_to_speech("Voice mode activated")
                    print("Voice mode activated. Say something!")
                    break
                else:
                    continue
            except LookupError:
                continue   # For ignoring if your are not speaking anything.
        except sr.UnknownValueError:
            continue  # For ignoring the unreconized words error

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
                _jarvis.speech.text_to_speech("Listening stopped.")
                break
            else:
                print(pinger)
                if listen:
                    line = pinger
                    jarvis.eval(line)

        except LookupError:
            _jarvis.speech.text_to_speech('Audio cannot be read!')
            print("Could not understand audio")
            _jarvis.speech.text_to_speech("unable to recognize voice")
        except sr.UnknownValueError:
            continue
        except sr.RequestError:
            print("Could not request results from Google Recognition service")
            continue  # It will ignore connecting server error.
