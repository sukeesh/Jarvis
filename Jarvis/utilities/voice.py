"""
ABOUT: 
This class is the Voice of Jarvis. The methods included in this class 
generate audio output of Jarvis while interacting with the user.
DOCUMENTATION on gtts:
https://github.com/pndurette/gTTS
"""
import os
from gtts import gTTS


class Voice:
    def __init__(self):
        """
        This constructor creates a gTTS instance .
        """
        self.tts_engine = gTTS(text=' ')

    def create(self):
        """
        This method creates a pyttsx object.
        :return: Nothing to return.
        """
        raise NotImplementedError

    def destroy(self):
        """
        This method destroys a pyttsx object in order
        to create a new one in the next interaction.
        :return: Nothing to return.
        """
        raise NotImplementedError

    def speak(self):
        """
        This method must be invoked whenever Jarvis is ready to
        get a command by its user.
        :return: None.
        """
        self.text_to_speech('What can I do for you?')

    def text_to_speech(self, speech):
        """
        This method converts a text to speech.
        :param speech: The text we want Jarvis to generate as audio
        :return: Nothing to return.
        """
        self.tts_engine = gTTS(text=speech, lang='en')
        self.tts_engine.save(savefile='curr_command.mp3')
        os.system('mpg321 curr_command.mp3 2> /dev/null')

"""
    The following block of code is a test for this class.
    In order to execute it run this script from the terminal
    as: ~$ python Voice.py
"""

if __name__ == '__main__':
    jarvis = Voice()
    jarvis.speak()
    text = ['Say hello to my little friend', 'What time is it',
            'Welcome to Jarvis', 'I am trolling you']
    for _ in text:
        jarvis.text_to_speech(_)
