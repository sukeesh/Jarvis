from io import BytesIO
import tempfile
from plugin import plugin, require, alias
from colorama import Fore
from shazamio import Shazam
import pydub
import asyncio

requirements = ['ffmpeg']
try:
    import pyaudio
    import speech_recognition as sr
except ImportError:
    requirements.append(
        'voice_control_requirements (install portaudio + re-run setup.sh)')


@require(network=True, native=requirements)
@alias("shazam")
@plugin("music recognition")
class MusicRecognition:
    """A tool to recognize music through Shazam API."""

    def __init__(self):
        self.sound_recorded = None
        self.shazam = Shazam()

    def __call__(self, jarvis, s):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.music_recognition(jarvis))
        

    async def music_recognition(self, jarvis):
        """Main function.

        This function is the main menu, that will run
        until the user says otherwise.
        """

        jarvis.say('')
        jarvis.say('This tool will help you compress a image')

        r = sr.Recognizer()

        print(sr.Microphone.list_microphone_names())

        my_mic = sr.Microphone(device_index=1)
        
        with my_mic as source:

            print('-----Now Recording-----')

            audio = r.record(source=source, duration=5)


            wav_file = pydub.AudioSegment.from_file(
                file=BytesIO(audio.get_wav_data()), format="wav")

            fp = tempfile.NamedTemporaryFile()

            wav_file.export(fp, format="mp3")

            mp3_file = pydub.AudioSegment.from_file(fp)
            pydub.playback.play(mp3_file)
    
            out = await self.shazam.recognize_song(fp.name)
            print(out)
