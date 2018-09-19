from utilities.GeneralUtilities import IS_MACOS


if IS_MACOS:
    from os import system
else:
    import pyttsx3

def create_voice():
    if IS_MACOS:
        return VoiceMac()
    else:
        try:
            return VoiceLinux()
        except OSError:
            return VoiceNotSupported()


class Voice:
    """
    ABOUT: This class is the Voice of Jarvis.
        The methods included in this class
        generate audio output of Jarvis while
        interacting with the user.
    DOCUMENTATION on pyttsx3:
        https://pyttsx3.readthedocs.io/en/latest/
    """
    def speak(self, first_run):
        """
        This method must be invoked whenever Jarvis is ready to
        get a command by its user.
        :param first_run: notifies Jarvis if this is the
                          if this is the first interaction with
                          the user. If so it says "Hi" to him.
        :return: Nothing to return.
        """
        if first_run:
            self.text_to_speech('Hi, what can I do for you?')
        else:
            self.text_to_speech('What can i do for you?')


class VoceMac(Voice):
    def text_to_speech(self, speech):
        system('say {}'.format(speech))


class VoiceLinux(Voice):
    def __init__(self):
        """
        This constructor creates a pyttsx3 object.
        """
        self.create()
        self.engine = None

    def create(self):
        """
        This method creates a pyttsx3 object.
        :return: Nothing to return.
        """
        self.engine = pyttsx3.init()
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
        self.create()
        self.engine.say(speech)
        self.engine.runAndWait()
        self.destroy()


class VoiceNotSupported(Voice):
    def __init__(self):
        self.warning_print = False

    def text_to_speech(self, speech):
        if not self.warning_print:
            print("Speech not supported! Please install pyttsx3 text-to-speech engine (sapi5, nsss or espeak)")
            self.warning_print = True
