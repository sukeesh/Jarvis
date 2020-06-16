from colorama import Fore

from packages.memory.memory import Memory
from utilities import schedule
from utilities.animations import SpinnerThread
from utilities.notification import notify
from utilities.voice import create_voice


class DummyIO:
    def say(self, text, color=''):
        pass

    def inptu(self, prompt="", color=""):
        pass

    def exit(self):
        pass


class JarvisAPI:
    """
    Jarvis interface for plugins.

    Plugins will receive a instance of this as the second (non-self) parameter
    of the exec()-method.

    Everything Jarvis-related that can't be implemented as a stateless-function
    in the utilities-package should be implemented here.
    """

    _CONNECTION_ERROR_MSG = "You are not connected to Internet"

    def __init__(self):
        self.spinner_running = False

        self.memory = Memory()
        self.scheduler = schedule.Scheduler()

        # Remember voice settings
        self.enable_voice = self.get_data('enable_voice')
        self.speech_rate = self.get_data('speech_rate')

        if not self.speech_rate:
            self.speech_rate = 120

        # what if the platform does not have any engines, travis doesn't have sapi5 acc to me
        try:
            gtts_status = self.get_data('gtts_status')
            self.speech = create_voice(self, gtts_status, rate=self.speech_rate)
        except Exception as e:
            self.say("Voice not supported", self, Fore.RED)
            self.say(str(e), self, Fore.RED)

        self.io = DummyIO()

    def say(self, text, color="", speak=True):
        """
        This method give the jarvis the ability to print a text
        and talk when sound is enable.
        :param text: the text to print (or talk)
        :param color: for text - use colorama (https://pypi.org/project/colorama/)
                      e.g. Fore.BLUE
        :param speak: False-, if text shouldn't be spoken even if speech is enabled
        """
        self.io.say(text, color)
        if speak:
            self._speak(text)

    def input(self, prompt="", color=""):
        """
        Get user input
        """
        self.io.input(prompt, color)

    def exit(self):
        """Immediately exit Jarvis"""
        self.io.exit()

    def _speak(self, text):
        if self.enable_voice:
            self.speech.text_to_speech(text)

    def input_number(self, prompt="", color="", rtype=float, rmin=None, rmax=None):
        """
        Get user input: As number.

        Guaranteed only returns number - ask user till correct number entered.

        :param prompt: Printed to console
        :param color: Color of prompot
        :param rtype: type of return value; e.g. float (default) or int
        :param rmin: Minum of values returned
        :param rmax: Maximum of values returned
        """
        while True:
            try:
                value = rtype(self.input(prompt, color).replace(',', '.'))
                if (rmin is not None and value < rmin) or (rmax is not None and value > rmax):
                    prompt = "Sorry, needs to be between {} and {}. Try again: ".format(rmin, rmax)
                else:
                    return value
            except ValueError:
                prompt = 'Sorry, needs to be a number. Try again: '
                continue

    def connection_error(self):
        """Print generic connection error"""

        if self.is_spinner_running():
            self.spinner_stop('')

        self.say(JarvisAPI._CONNECTION_ERROR_MSG)

    def notification(self, msg, time_seconds=0):
        """
        Sends notification msg in time_in milliseconds
        :param msg: Message. Either String (message body) or tuple (headline, message body)
        :param time_seconds: Time in seconds to wait before showing notification
        """
        if isinstance(msg, tuple):
            headline, message = msg
        elif isinstance(msg, str):
            headline = "Jarvis"
            message = msg
        else:
            raise ValueError("msg not a string or tuple")

        if time_seconds == 0:
            notify(headline, message)
        else:
            schedule(time_seconds, notify, headline, message)

    def schedule(self, time_seconds, function, *args):
        """
        Schedules function
        After time_seconds call function with these parameter:
           - reference to this JarvisAPI instance
           - schedule_id (return value of this function)
           - *args
        :return: integer, id - use with cancel
        """
        return self.scheduler.create_event(
            time_seconds, function, self, *args)

    def cancel(self, schedule_id):
        """
        Cancel event scheduled with schedule
        :param schedule_id: id returned by schedule
        """
        spinner = SpinnerThread('Cancelling', 0.15)
        spinner.start()

        self.scheduler.cancel(schedule_id)

        spinner.stop()
        self.say('Cancellation successful', Fore.GREEN)

    # Voice wrapper
    def enable_voice(self):
        """
        Use text to speech for every text passed to jarvis.say()
        """
        g = self.get_data('gtts_status')
        self.speech = create_voice(self, g, rate=120)
        self.enable_voice = True
        self.update_data('enable_voice', True)

    def disable_gtts(self):
        """
        Switch to default speech engine for every text passed to jarvis.say()
        """
        self.update_data('gtts_status', False)

    def enable_gtts(self):
        """
        Use google text to speech for every text passed to jarvis.say()
        """
        self.update_data('gtts_status', True)
        g = self.get_data('gtts_status')
        self.speech = create_voice(self, g, rate=120)

    def disable_voice(self):
        """
        Stop text to speech output & disable gtts for every text passed to jarvis.say()
        """
        self.disable_gtts()
        self.enable_voice = False
        self.update_data('enable_voice', False)

    def is_voice_enabled(self):
        """
        Returns True/False if voice is enabled/disabled with
        enable_voice or disable_voice
        Default: False (disabled)
        """
        return self.enable_voice

    def change_speech_rate(self, delta):
        """
        Alters the rate of the speech engine by a specified amount and remember
        the new speech rate.
        :param delta: Amount of change to apply to speech rate
        """
        self.speech.change_rate(delta)
        self.update_data('speech_rate', self.speech.rate)

    # MEMORY WRAPPER
    def get_data(self, key):
        """
        Get a specific key from memory
        """
        return self.memory.get_data(key)

    def add_data(self, key, value):
        """
        Add a key and value to memory
        """
        self.memory.add_data(key, value)
        self.memory.save()

    def update_data(self, key, value):
        """
        Updates a key with supplied value.
        """
        self.memory.update_data(key, value)
        self.memory.save()

    def del_data(self, key):
        """
        Delete a key from memory
        """
        self.memory.del_data(key)
        self.memory.save()

    def eval(self, s):
        """
        Simulates typing 's' in Jarvis prompt
        """
        line = self._jarvis.precmd(s)
        stop = self._jarvis.onecmd(line)
        stop = self._jarvis.postcmd(stop, line)
        # TODO

    def spinner_start(self, message="Starting "):
        """
        Function for starting a spinner when prompted from a plugin
        and a default message for performing the task
        """
        self.spinner_running = True
        self.spinner = SpinnerThread(message, 0.15)
        self.spinner.start()

    def spinner_stop(self, message="Task executed successfully! ", color=Fore.GREEN):
        """
        Function for stopping the spinner when prompted from a plugin
        and displaying the message after completing the task
        """
        self.spinner.stop()
        self.say(message, color)
        self.spinner_running = False

    def is_spinner_running(self):
        return self.spinner_running
