import socket
import struct
from dependency import require
GTTS_KEY = 'gtts_status'


@require(imports=['speech_recognition', 'pvporcupine', 'pyaudio'])
class VoiceControl:
    QUALITY = 1

    def __init__(self, jarvis):
        self.jarvis = jarvis
        self.listen = True

    def get_name():
        return 'Voice control'

    def start(self):
        import pvporcupine
        import pyaudio
        import speech_recognition as sr

        keyword = 'jarvis'

        porcupine = pvporcupine.create(
            library_path=pvporcupine.LIBRARY_PATH,
            model_path=pvporcupine.MODEL_PATH,
            keyword_paths=[pvporcupine.KEYWORD_PATHS[keyword]],
            sensitivities=[0.5]
        )

        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
            input_device_index=None)

        r = sr.Recognizer()
        connected = self.jarvis.has_internet()

        self.jarvis.say("LISTEN")

        while self.listen is True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm)
            if result >= 0:
                self.jarvis.say("I'm listening")

                try:
                    with sr.Microphone() as source:
                        r.adjust_for_ambient_noise(source)
                        audio = r.listen(source)

                        if connected and self.jarvis.get_data(GTTS_KEY) is not False:
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
