import socket

voice_control_installed = True
try:
    import speech_recognition as sr
except ImportError:
    voice_control_installed = False

if voice_control_installed:
    requirements = []
else:
    requirements = [
        'voice_control_requirements (install portaudio + re-run setup.sh)']


class VoiceControl:
    def __init__(self, jarvis):
        self.jarvis = jarvis
        self.listen = True

    def start(self):
        r = sr.Recognizer()

        connected = jarvis.has_internet()

        while self.listen is True:
            while True:
                try:
                    print("LISTEN")
                    with sr.Microphone() as source:
                        r.energy_threshold = 50
                        r.adjust_for_ambient_noise(source, duration=2)  # Eleminating the noise.
                        try:
                            audio = r.listen(source, phrase_time_limit=0.2)  # Storing audio.
                        except sr.WaitTimeoutError as e:
                            print("retry")
                            continue

                        print('5')

                        if not self.listen:
                            return

                        # google recognition disabled for jarvis recognition
                        pinger = r.recognize_sphinx(audio)

                    try:
                        print(pinger)
                        if (pinger.lower() == "jarvis"):
                            self.jarvis.say("I'm listening")
                            break
                        print(pinger.lower())
                    except LookupError as e:
                        print(e)
                        continue   # For ignoring if your are not speaking anything.
                except sr.UnknownValueError as e:
                    print(e)
                    continue  # For ignoring the unreconized words error

            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)
                    audio = r.listen(source)

                    if connected:
                        pinger = r.recognize_google(audio).lower()

                    else:
                        pinger = r.recognize_sphinx(audio).lower()

                    print(pinger)
                    line = pinger
                    self.jarvis.execute_once(line)

            except LookupError:
                self.jarvis.say.say('Audio cannot be read!')
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                self.jarvis.say("Could not request results from Google Recognition service")
                continue  # It will ignore connecting server error.

    def say(self, *args):
        # Voice control cannot say anything
        pass

    def show_prompt(self):
        pass

    def stop(self):
        self.listen = False

    def input(self, prompt="", color=""):
        pass
