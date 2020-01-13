import re
from utilities.GeneralUtilities import IS_MACOS, IS_WIN


if IS_MACOS:
    from os import system
else:
    import pyttsx3


# TODO: Add rate for all platforms
def create_voice(rate=120):
    """
    :param rate: Speech rate for the engine
    """
    if IS_MACOS:
        return VoiceMac()
    elif IS_WIN:
        return VoiceWin()
    else:
        try:
            return VoiceLinux(rate)
        except OSError:
            return VoiceNotSupported()


def remove_ansi_escape_seq(text):
    """
    This method removes ANSI escape sequences (such as a colorama color
    code) from a string so that they aren't spoken.

    :param text: The text that may contain ANSI escape sequences.
    :return: The text with ANSI escape sequences removed.
    """
    if text:
        text = re.sub(r'''(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]''', '', text)
    return text


# class Voice:
#     """
#     ABOUT: This class is the Voice of Jarvis.
#         The methods included in this class
#         generate audio output of Jarvis while
#         interacting with the user.
#     DOCUMENTATION on pyttsx3:
#         https://pyttsx3.readthedocs.io/en/latest/
#     """


class VoiceMac():
    def text_to_speech(self, speech):
        speech = remove_ansi_escape_seq(speech)
        speech = speech.replace("'", "\\'")
        system('say $\'{}\''.format(speech))


class VoiceLinux():
    def __init__(self, rate):
        """
        This constructor creates a pyttsx3 object.
        """
        self.create(rate)

    def create(self, rate):
        """
        This method creates a pyttsx3 object.
        :param rate: Speech rate for the engine.
        :return: Nothing to return.
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)

    def destroy(self):
        """
        This method destroys a pyttsx3 object in order
        to create a new one in the next interaction.
        :return: Nothing to return.
        """
        del self.engine

    def text_to_speech(self, speech):
        """
        This method converts a text to speech.
        :param speech: The text we want Jarvis to generate as audio
        :return: Nothing to return.

        A bug in pyttsx3 causes segfault if speech is '', so used 'if' to avoid that.
        """
        if speech != '':
            speech = remove_ansi_escape_seq(speech)
            self.engine.say(speech)
            self.engine.runAndWait()
            self.engine.stop()

    def change_rate(self, delta):
        """
        This method modifies the rate of the speech engine.
        :param delta: The amount to modify the rate from the current rate.
        :return: The updated speech rate.
        """
        current_rate = self.engine.getProperty('rate')
        new_rate = current_rate + delta
        self.engine.setProperty('rate', new_rate)
        return new_rate


class VoiceWin():
    def __init__(self):
        """
        This constructor creates a pyttsx3 object.
        """
        self.create()

    def create(self):
        """
        This method creates a pyttsx3 object.
        :return: Nothing to return.
        """
        self.engine = pyttsx3.init("sapi5")
        self.engine.setProperty('rate', 120)

    def destroy(self):
        """
        This method destroys a pyttsx3 object in order
        to create a new one in the next interaction.
        :return: Nothing to return.
        """
        del self.engine

    def text_to_speech(self, speech):
        """
        This method converts a text to speech.
        :param speech: The text we want Jarvis to generate as audio
        :return: Nothing to return.
        """
        speech = remove_ansi_escape_seq(speech)
        self.create()
        self.engine.say(speech)
        self.engine.runAndWait()
        self.destroy()


class VoiceNotSupported():
    def __init__(self):
        self.warning_print = False

    def text_to_speech(self, speech):
        if not self.warning_print:
            print(
                "Speech not supported! Please install pyttsx3 text-to-speech engine (sapi5, nsss or espeak)")
            self.warning_print = True
