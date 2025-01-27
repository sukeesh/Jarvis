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
    r = sr.Recognizer()
    _jarvis = jarvis._jarvis
    
    def listen_for_command(source):
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        return r.recognize_google(audio).lower()
    
    def activate_voice_mode():
        _jarvis.speech.text_to_speech("Say listen to start voice mode")
        while True:
            try:
                with sr.Microphone() as source:
                    os.system('reset')
                    print("Say listen to start listening")
                    command = listen_for_command(source)
                    if command == "listen":
                        _jarvis.speech.text_to_speech("Voice mode activated")
                        print("Voice mode activated. Say something!")
                        return True
            except (sr.UnknownValueError, LookupError):
                continue
    
    def process_commands():
        while True:
            print("Say something")
            try:
                with sr.Microphone() as source:
                    command = listen_for_command(source)
                    if command == "stop":
                        _jarvis.speech.text_to_speech("Listening stopped.")
                        print("Listening stopped.")
                        return
                    print(command)
                    jarvis.eval(command)
            except LookupError:
                _jarvis.speech.text_to_speech('Audio cannot be read!')
                print("Could not understand audio")
                _jarvis.speech.text_to_speech("unable to recognize voice")
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                print("Could not request results from Google Recognition service")
                continue

    if activate_voice_mode():
        process_commands()
