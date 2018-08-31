import signal

from os import system
from cmd import Cmd
from time import ctime
from platform import architecture, dist, release, system as sys
from functools import partial

import six

from requests import ConnectionError
from six.moves import input

from colorama import Fore
from PluginManager import PluginManager

from packages import (directions_to, forecast, mapps, movie, near_me, picshow,
                      timeIn, translate, weather_pinpoint, weatherIn)
from packages.news import News
from packages.imgur import imgur
from packages.quote import show_quote
from packages.lyrics import lyrics
from packages.cricket import score
from packages.tempconv import temp_main
from packages.dictionary import dictionary
from packages.currencyconv import currencyconv, find_currencies, get_currency
from packages.file_organise import file_manage
from packages.systemOptions import turn_off_screen, update_system
from packages.memory.memory import Memory

from utilities import schedule
from utilities.voice import create_voice
from utilities.notification import notify
from utilities.GeneralUtilities import (get_float, IS_MACOS, MACOS, print_say,
                                        unsupported)


CONNECTION_ERROR_MSG = "You are not connected to Internet"


class JarvisAPI(object):
    """
    Jarvis interface for plugins.

    Plugins will receive a instance of this as the second (non-self) parameter
    of the exec()-method.

    Everything Jarvis-related that can't be implemented as a stateless-function
    in the utilities-package should be implemented here.
    """

    CONNECTION_ERROR_MSG = "You are not connected to Internet"

    def __init__(self, jarvis):
        self._jarvis = jarvis

    def say(self, text, color=""):
        """
        This method give the jarvis the ability to print a text
        and talk when sound is enable.
        :param text: the text to print (or talk)
               color: Fore.COLOR (ex Fore.BLUE), color for text
        :return: Nothing to return.
        """
        self._jarvis.speak(text)
        print(color + text + Fore.RESET)

    def connection_error(self):
        """Print generic connection error"""
        self.say(JarvisAPI.CONNECTION_ERROR_MSG)

    def exit(self):
        self._jarvis.close()

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
           - schedule_id (return value of this fuction)
           - *args
        :return: integer, id - use with cancel
        """
        return self._jarvis.scheduler.create_event(time_seconds, function, self, *args)

    def cancel(self, schedule_id):
        """
        Cancel event scheduled with schedule
        :param schedule_id: id returned by schedule
        """
        self._jarvis.scheduler.cancel(schedule_id)

    # MEMORY WRAPPER
    def get_data(self, key):
        """
        get a specific key from memory
        """
        return self._jarvis.memory.get_data(key)

    def add_data(self, key, value):
        """
        add a key and value to memory
        """
        self._jarvis.memory.add_data(key, value)
        self._jarvis.memory.save()

    def update_data(self, key, value):
        """
        Updates a key with supplied value.
        """
        self._jarvis.memory.update_data(key, value)
        self._jarvis.memory.save()

    def del_data(self, key):
        """
        delete a key from memory
        """
        self._jarvis.memory.del_data(key)
        self._jarvis.memory.save()


class CmdInterpreter(Cmd):
    # We use this variable at Breakpoint #1.
    # We use this in order to allow Jarvis say "Hi", only at the first
    # interaction.

    # This can be used to store user specific data

    def __init__(self, first_reaction_text, prompt, directories=[], first_reaction=True, enable_voice=False):
        """
        This constructor contains a dictionary with Jarvis Actions (what Jarvis can do).
        In alphabetically order.
        """
        Cmd.__init__(self)
        self.first_reaction = first_reaction
        self.first_reaction_text = first_reaction_text
        self.prompt = prompt
        self.enable_voice = enable_voice
        # Register do_quit() function to SIGINT signal (Ctrl-C)
        signal.signal(signal.SIGINT, self.interrupt_handler)

        self.memory = Memory()
        self.scheduler = schedule.Scheduler()
        self.speech = create_voice()

        self.actions = [{"check": ("ram", "weather", "time", "forecast")},
                        "cricket",
                        {"decrease": ("volume",)},
                        "dictionary",
                        "directions",
                        {"disable": ("sound",)},
                        {"display": ("pics",)},
                        {"enable": ("sound",)},
                        "file_organise",
                        "help",
                        {"hotspot": ("start", "stop")},
                        "how_are_you",
                        "imgur",
                        "lyrics",
                        "match",
                        {"movie": ("cast", "director", "plot", "producer", "rating", "year",)},
                        "movies",
                        "near",
                        "news",
                        {"open": ("camera",)},
                        "pinpoint",
                        "quote",
                        "currencyconv",
                        "say",
                        "tempconv",
                        "translate",
                        "umbrella",
                        {"update": ("location", "system")},
                        "weather",
                        ]

        self.fixed_responses = {"what time is it": "clock",
                                "where am i": "pinpoint",
                                "how are you": "how_are_you"
                                }

        self._api = JarvisAPI(self)
        self._plugin_manager = PluginManager()

        for directory in directories:
            self._plugin_manager.add_directory(directory)

        self._activate_plugins()

    def _activate_plugins(self):
        """Generate do_XXX, help_XXX and (optionally) complete_XXX functions"""
        for (plugin_name, plugin) in self._plugin_manager.get_all().items():
            completions = self._plugin_update_action(plugin, plugin_name)
            if completions is not None:
                def complete(completions):
                    def _complete_impl(self, text, line, begidx, endidx):
                        return [i for i in completions if i.startswith(text)]
                    return _complete_impl
                setattr(CmdInterpreter, "complete_" + plugin_name, complete(completions))
            setattr(CmdInterpreter, "do_" + plugin_name, partial(plugin.run, self._api))
            setattr(CmdInterpreter, "help_" + plugin_name, partial(self._api.say, plugin.get_doc()))

            if hasattr(plugin.__class__, "init") and callable(getattr(plugin.__class__, "init")):
                plugin.init(self._api)

    def _plugin_update_action(self, plugin, plugin_name):
        """Return True if completion is available"""
        complete = plugin.complete()
        if complete is not None:
            # add plugin with completion
            # Dictionary:
            # { plugin_name : list of completions }
            complete = [x for x in complete]
            self.actions.append({plugin_name: complete})
            return complete
        else:
            # add plugin without completion
            # plugin name only
            self.actions.append(plugin_name)
            return None

    def close(self):
        """Closing Jarvis."""
        print_say("Goodbye, see you later!", self, Fore.RED)
        self.scheduler.stop_all()
        exit()

    def completedefault(self, text, line, begidx, endidx):
        """Default completion"""
        return [i for i in self.actions if i.startswith(text)]

    def error(self):
        """Jarvis let you know if an error has occurred."""
        print_say("I could not identify your command...", self, Fore.RED)

    def get_completions(self, command, text):
        """Returns a list with the completions of a command."""
        dict_target = [item for item in self.actions
                       if type(item) == dict and command in item][0]
        completions_list = dict_target[command]
        return [i for i in completions_list if i.startswith(text) and i != '']

    def interrupt_handler(self, signal, frame):
        """Closes Jarvis on SIGINT signal. (Ctrl-C)"""
        self.close()

    def do_calculate(self, s):
        """Jarvis will get your calculations done!"""
        tempt = s.replace(" ", "")
        if len(tempt) > 1:
            evaluator.calc(tempt, self)
        else:
            print_say("Error: Not in correct format", self, Fore.RED)

    def help_calculate(self):
        """Print help about calculate command."""
        print_say("Jarvis will get your calculations done!", self)
        print_say("-- Example:", self)
        print_say("\tcalculate 3 + 5", self)

    def do_check(self, s):
        """Checks your system's RAM stats."""
        # if s == "ram":
        if "ram" in s:
            system("free -lm")
        # if s == "time"
        elif "time" in s:
            timeIn.main(self, s)
        elif "forecast" in s:
            forecast.main(self, s)
        # if s == "weather"
        elif "weather" in s:
            try:
                weatherIn.main(self, s)
            except ConnectionError:
                print(CONNECTION_ERROR_MSG)

    def help_check(self):
        """Prints check command help."""
        print_say("ram: checks your system's RAM stats.", self)
        print_say("time: checks the current time in any part of the globe.", self)
        print_say(
            "weather in *: checks the current weather in any part of the globe.", self)
        print_say(
            "forecast: checks the weather forecast for the next 7 days.", self)
        print_say("-- Examples:", self)
        print_say("\tcheck ram", self)
        print_say("\tcheck time in Manchester (UK)", self)
        print_say("\tcheck weather in Canada", self)
        print_say("\tcheck forecast", self)
        print_say("\tcheck forecast in Madrid", self)
        # add here more prints

    def complete_check(self, text, line, begidx, endidx):
        """Completions for check command"""
        return self.get_completions("check", text)

    def do_cricket(self, s=None):
        """Jarvis will show current matches and their score for you"""
        try:
            score(self)
        except ConnectionError:
            print(CONNECTION_ERROR_MSG)

    def help_cricket(self):
        """cricket package for Jarvis"""
        print_say("Enter cricket and follow the instructions", self)

    def complete_decrease(self, text, line, begidx, endidx):
        """Completions for decrease command"""
        return self.get_completions("decrease", text)

    def do_dictionary(self, s):
        """Returns meaning, synonym and antonym of any english word"""
        dictionary(self)

    def help_dictionary(self):
        """Print help about dictionary feature"""
        print_say("Get meaning, synonym and antonym of any word", self)

    def do_directions(self, data):
        """Get directions about a destination you are interested to."""
        try:
            directions_to.main(data)
        except ValueError:
            print("Please enter destination")
        except ConnectionError:
            print(CONNECTION_ERROR_MSG)

    def help_directions(self):
        """Prints help about directions command"""
        print_say("Get directions about a destination you are interested to.", self)
        print_say("-- Example:", self)
        print_say("\tdirections to the Eiffel Tower", self)

    def do_disable(self, s):
        """Deny Jarvis to use his voice."""
        if "sound" in s:
            self.enable_voice = False

    def help_disable(self):
        """Displays help about disable command"""
        print_say("sound: Deny Jarvis his voice.", self)

    def complete_disable(self, text, line, begidx, endidx):
        """Completions for check command"""
        return self.get_completions("disable", text)

    def do_display(self, s):
        """Displays photos."""
        if "pics" in s:
            s = s.replace("pics", "").strip()
            picshow.showpics(s)

    def help_display(self):
        """Prints help about display command"""
        print_say("Displays photos of the topic you choose.", self)
        print_say("-- Example:", self)
        print_say("\tdisplay pics of castles", self)

    def complete_display(self, text, line, begidx, endidx):
        """Completions for display command"""
        return self.get_completions("display", text)

    def do_enable(self, s):
        """Let Jarvis use his voice."""
        if "sound" in s:
            self.enable_voice = True

    def help_enable(self):
        """Displays help about enable command"""
        print_say("sound: Let Jarvis use his voice.", self)

    def complete_enable(self, text, line, begidx, endidx):
        """Completions for enable command"""
        return self.get_completions("enable", text)

    def do_file_organise(self, s=None):
        """Jarvis will organise the given folder and group the files"""
        file_manage(self)

    def help_file_organise(self):
        """Help for file organise"""
        print_say("Type file_organise and follow instructions", self)
        print_say("It organises selected folder based on extension", self)

    @unsupported(platform=MACOS)
    def do_hotspot(self, s):
        """Jarvis will set up your own hotspot."""
        if "start" in s:
            system("sudo ap-hotspot start")
        elif "stop" in s:
            system("sudo ap-hotspot stop")

    @unsupported(platform=MACOS)
    def help_hotspot(self):
        """Print help about hotspot commando."""
        print_say("start: Jarvis will set up your own hotspot.", self)
        print_say("stop: Jarvis will stop your hotspot.", self)

    def complete_hotspot(self, text, line, begidx, endidx):
        """Completions for enable command"""
        return self.get_completions("hotspot", text)

    def do_how_are_you(self, s):
        """Jarvis will inform you about his status."""
        print_say("I am fine, How about you?", self, Fore.BLUE)

    def help_how_are_you(self):
        """Print info about how_are_you command"""
        print_say("Jarvis will inform you about his status.", self)

    def do_lyrics(self, s):
        # TODO: maybe add option to download lyrics not just print them there
        lyr = lyrics()
        response = lyr.find(s)
        print_say(response, self)

    def help_lyrics(self):
        """explains how lyrics work"""
        print_say("finds lyrics\n", self)
        print_say("the format is song,artist\n", self)
        print_say("song and artist are separated by a - \n", self)
        print_say("-- Example:", self)
        print_say("\tlyrics wonderful tonight-eric clapton", self)

    def do_match(self, s):
        """Matches patterns in a string by using regex."""
        file_name = input(Fore.RED + "Enter file name?:\n" + Fore.RESET)
        pattern = input(Fore.GREEN + "Enter string:\n" + Fore.RESET)
        file_name = file_name.strip()
        if file_name == "":
            print("Invalid Filename")
        else:
            system("grep '" + pattern + "' " + file_name)

    def help_match(self):
        """Prints help about match command"""
        print_say("Matches a string pattern in a file using regex.", self)
        print_say("Type \"match\" and you'll be prompted.", self)

    def do_movie(self, s):
        """Jarvis will get movie details for you"""
        k = s.split(' ', 1)
        if k[0] == "cast":
            data = movie.cast(k[1])
            for d in data:
                print_say(d['name'], self)
        elif k[0] == "director":
            data = movie.director(k[1])
            for d in data:
                print_say(d['name'], self)
        elif k[0] == "plot":
            data = movie.plot(k[1])
            print_say(data, self)
        elif k[0] == "producer":
            data = movie.producer(k[1])
            for d in data:
                print_say(d['name'], self)
        elif k[0] == "rating":
            data = movie.rating(k[1])
            print_say(str(data), self)
        elif k[0] == "year":
            data = movie.year(k[1])
            print_say(str(data), self)

    def help_movie(self):
        """Print help about movie command."""
        print_say("Jarvis - movie command", self)
        print_say("List of commands:", self)
        print_say("movie cast", self)
        print_say("movie director", self)
        print_say("movie plot", self)
        print_say("movie producer", self)
        print_say("movie rating", self)
        print_say("movie year", self)

    @unsupported(platform=MACOS)
    def do_movies(self, s):
        """Jarvis will find a good movie for you."""
        movie_name = input(
            Fore.RED + "What do you want to watch?\n" + Fore.RESET)
        system("ims " + movie_name)

    @unsupported(platform=MACOS)
    def help_movies(self):
        """Print help about movies command."""
        print_say("Jarvis will find a good movie for you", self)

    def do_near(self, data):
        """Jarvis can find what is near you!"""
        near_me.main(data)

    def help_near(self):
        """Print help about near command."""
        print_say("Jarvis can find what is near you!", self)
        print_say("-- Examples:", self)
        print_say("\trestaurants near me", self)
        print_say("\tmuseums near the eiffel tower", self)

    def do_news(self, s):
        """Time to get an update about the local news."""
        if s == "quick":
            try:
                n = News()
                n.quick_news()
            except:
                print_say("I couldn't find news", self, Fore.RED)
        else:
            try:
                n = News()
                n.news()
            except:
                print_say("I couldn't find news", self, Fore.RED)

    def help_news(self):
        """Print help about news command."""
        print_say("Time to get an update about the local news.", self)
        print_say(
            "Type \"news\" to choose your source or \"news quick\" for some headlines.", self)

    def do_open(self, s):
        """Jarvis will open the camera for you."""
        if "camera" in s:
            if IS_MACOS:
                system('open /Applications/Photo\ Booth.app')
            else:
                print_say("Opening cheese.......", self, Fore.RED)
                system("cheese")

    def help_open(self):
        """Print help about open command."""
        print_say("camera: Jarvis will open the camera for you.", self)

    def complete_open(self, text, line, begidx, endidx):
        """Completions for open command"""
        return self.get_completions("open", text)

    def do_pinpoint(self, s):
        """Jarvis will pinpoint your location."""
        try:
            mapps.locate_me()
        except ConnectionError:
            print(CONNECTION_ERROR_MSG)

    def help_pinpoint(self):
        """Print help about pinpoint command."""
        print_say("Jarvis will pinpoint your location.", self)

    def do_quote(self, s=None):
        """Show quote of the day or quotes based on a gven word"""
        show_quote(self)

    def help_quote(self):
        """Help for quote"""
        print_say("quote prints quote for the day for you" +
                  "or quotes based on a given keyword", self)

    def do_currencyconv(self, s=None):
        """Show the convert from a currency to another"""
        currencies = find_currencies()

        amount = get_float('Enter an amount: ')
        from_currency = get_currency('Enter from which currency: ', currencies)
        to_currency = get_currency('Enter to which currency: ', currencies)

        currencyconv(self, amount, from_currency, to_currency)

    def help_currencyconv(self):
        """Help for currencyConverter"""
        print_say("Convert an amount of money from a currency to another.",
                  self)
        print_say("-- Type currencyconv, press enter and follow the" +
                  "instructions!", self)

    def do_say(self, s):
        """Reads what is typed."""
        if not s:
            print_say("What should I say?", self)
        else:
            voice_state = self.enable_voice
            self.enable_voice = True
            self.speech.text_to_speech(s)
            self.enable_voice = voice_state

    def help_say(self):
        """Prints help text from say command."""
        print_say("Reads what is typed.")

    def do_tempconv(self, s):
        """Convert temperature from Celsius to Fahrenheit or vice versa"""
        temp_main(self, s)

    def help_tempconv(self):
        """Print help information for tempconv command."""
        print_say("Convert temperature from Fahrenheit to Celsius and vice versa", self)
        print_say("Examples: 32f, 18C, -20F, -8c, 105.4F, -10.21C", self)

    def do_translate(self, s):
        """Translates text from one language (source) to another(destination)"""
        translate.main(self)

    def help_translate(self):
        """Print help for translate function"""
        print_say("translates from one language to another.", self)

    def do_umbrella(self, s):
        """If you're leaving your place, Jarvis will inform you if you might need an umbrella or not"""
        s = 'umbrella'
        try:
            weather_pinpoint.main(self.memory, self, s)
        except ConnectionError:
            print(CONNECTION_ERROR_MSG)

    def help_umbrella(self):
        """Print info about umbrella command."""
        print_say(
            "If you're leaving your place, Jarvis will inform you if you might need an umbrella or not.", self,
            Fore.BLUE)

    def do_update(self, s):
        """Updates location or system."""
        if "location" in s:
            location = self.memory.get_data('city')
            loc_str = str(location)
            print_say("Your current location is set to " + loc_str, self)
            print_say("What is your new location?", self)
            i = input()
            self.memory.update_data('city', i)
            self.memory.save()
        elif "system" in s:
            update_system()

    def help_update(self):
        """Prints help about update command"""
        print_say("location: Updates location.", self)
        print_say("system: Updates system.", self)

    def complete_update(self, text, line, begidx, endidx):
        """Completions for update command"""
        return self.get_completions("update", text)

    def do_weather(self, s):
        """Get information about today's weather."""
        try:
            weather_pinpoint.main(self.memory, self, s)
        except ConnectionError:
            print(CONNECTION_ERROR_MSG)

    def help_weather(self):
        """Prints help about weather command."""
        print_say(
            "Get information about today's weather in your current location.", self)

    def do_imgur(self, s):
        """Uploads image to imgur"""
        imgur(self, s)

    def help_imgur(self):
        """Prints help about imgur command"""
        print_say("Uploads an image to imgur", self)
        print_say("use imgur <image>", self)
