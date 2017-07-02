import pyttsx

'''
    ABOUT: This class is the Voice of Jarvis.
           The methods included in this class
           generate audio output of Jarvis while
           interacting with the user.
    DOCUMENTATION on pyttsx:
           https://pyttsx.readthedocs.io/en/latest/
'''


class Voice:
    def __init__(self):
        """
        This constructor creates a pyttsx object.
        """
        self.create()
        self.engine = None

    def create(self):
        """
        This method creates a pyttsx object.
        :return: Nothing to return.
        """
        self.engine = pyttsx.init()
        self.engine.setProperty('rate', 120)

    def destroy(self):
        """
        This method destroys a pyttsx object in order
        to create a new one in the next interaction.
        :return: Nothing to return.
        """
        del self.engine

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
            self.engine.say('Hi, what can i do for you?')
            self.engine.runAndWait()
            self.destroy()
        else:
            self.create()
            self.engine.say('What can i do for you?')
            self.engine.runAndWait()
            self.destroy()

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


'''
    The following block of code is a test for this class.
    In order to execute it run this script from the terminal
    as: ~$ python Voice.py
'''

if __name__ == '__main__':
    jarvis = Voice()
    jarvis.speak(True)
    text = ['Say hello to my little friend', 'What time is it',
            'Welcome to Jarvis', 'I am trolling you']
    for _ in text:
        jarvis.text_to_speech(_)
