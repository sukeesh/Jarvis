from plugin import plugin, require
from googletrans.constants import LANGCODES, LANGUAGES, SPECIAL_CASES
from googletrans import Translator

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
class Hear():
    def __call__(self, jarvis, s):
        r = sr.Recognizer()  # intializing the speech_recognition
        listen = False
        _jarvis = jarvis._jarvis  # calling jarvis object.
        print("Say your language")
        _jarvis.speech.text_to_speech("Say your language", "en")  # Prompt the user for a language.
        while listen is False:
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)    # Adjusts for background noise.
                    audio = r.listen(source)  # Storing audio.
                    dest = r.recognize_google(audio).lower()
                    print(dest)
                # The if-statements check for valid language.
                if dest in SPECIAL_CASES:
                    dest = SPECIAL_CASES[dest]
                    listen = True
                elif dest in LANGCODES:
                    dest = LANGCODES[dest]
                    listen = True
                else:
                    jarvis.say("\nInvalid source language\nTry again")

                if listen is True:
                    if dest == "en":
                        self.english(jarvis, _jarvis, r)
                    else:
                        self.other_lang(jarvis, _jarvis, r, dest)
            except sr.UnknownValueError:
                continue  # For ignoring the unrecognized words error

    # The english function will run the program without calls to translate.

    def english(self, jarvis, _jarvis, r):
        start_up = "Voice mode activated in english, say stop to stop listening"
        print(start_up)
        _jarvis.speech.text_to_speech(start_up, "en")
        _jarvis.speech.text_to_speech("What can I do for you?", lang="en")
        listen = True
        while listen is True:
            print("What can I do for you?")
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source)
                    pinger = r.recognize_google(audio).lower()
                    print(pinger)
                # Program will stop if word 'stop' is recognized.
                if pinger == "stop":
                    listen = False
                    print("Listening Stopped")
                    _jarvis.speech.text_to_speech("Listening stopped", lang="en")
                    break
                else:
                    if listen:
                        line = pinger
                        jarvis.eval(line)
            except LookupError:
                _jarvis.speech.text_to_speech("Cannot understand command", lang=dest)
            except sr.UnknownValueError:
                continue  # For ignoring when user is not speaking.
            except sr.RequestError:
                print("Could not request results from Google Recognition service")
                continue  # It will ignore connecting server error.

    def other_lang(self, jarvis, _jarvis, r, dest):
        translator = Translator()
        # Start-up line translated then voiced.
        start_up = "Voice mode activated in language " + LANGUAGES[dest] + ", say stop to stop listening mode"
        start_up = translator.translate(start_up, dest=dest, src="en")
        start_up = u"""
        {text}
            """.strip().format(text=start_up.text)
        print(start_up)
        _jarvis.speech.text_to_speech(start_up, lang=dest)
        _jarvis.speech.text_to_speech("What can I do for you?", lang=dest)
        listen = True
        while listen is True:
            command_text = translator.translate("What can I do for you?", dest=dest, src="en")
            command_text = u"""
            {text}
                """.strip().format(text=command_text.text)
            print(command_text)
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source)
                    pinger = r.recognize_google(audio, language=dest)
                    print(pinger)
                    pinger = translator.translate(pinger, dest="en", src=dest)
                    pinger = u"""
                    {text}
                        """.strip().format(text=pinger.text)
                    pinger = pinger.lower()
                if pinger == "stop":
                    listen = False
                    stopped = translator.translate("Listening stopped", dest=dest, src="en")
                    stopped = u"""
                    {text}
                        """.strip().format(text=stopped.text)
                    print(stopped)
                    _jarvis.speech.text_to_speech(stopped, lang=dest)
                    break
                else:
                    if listen:
                        line = pinger
                        jarvis.eval(line)

            except LookupError:
                error_msg = translator.translate("Cannot understand command", dest=dest, src="en")
                error_msg = u"""
                {text}
                    """.strip().format(text=error_msg.text)
                _jarvis.speech.text_to_speech(error_msg, lang=dest)

            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                print("Could not request results from Google Recognition service")
                continue  # It will ignore connecting server error.
