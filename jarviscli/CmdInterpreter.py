from os import system
from cmd import Cmd
import signal
import six
from platform import system as sys
from platform import architecture, release, dist
from time import ctime
from colorama import Fore
from requests import ConnectionError

from utilities import voice
from utilities.GeneralUtilities import (
    IS_MACOS, MACOS, print_say, unsupported
)

from packages.lyrics import lyrics
from packages.music import play
from packages.todo import todoHandler
from packages.reminder import reminder_handler, reminder_quit
from packages import mapps, picshow, evaluator, forecast, wiki, movie
from packages import directions_to, near_me, weather_pinpoint, chuck, weatherIn, timeIn
from packages.memory.memory import Memory
from packages.shutdown import shutdown_system, cancel_shutdown, reboot_system
from packages.systemOptions import turn_off_screen, update_system
from packages.news import News
from packages.clear import clear_scr
from packages.file_organise import file_manage
from packages.fb import fb_login
from packages.twitter import twitter_login, twitter_tweet, twitter_end
from packages.cricket import score
from packages.quote import show_quote
from packages.hackathon import find_hackathon
from packages import translate
from packages.dictionary import dictionary
if six.PY2:
    from packages import chat
MEMORY = Memory()

CONNECTION_ERROR_MSG = "You are not connected to Internet"


class CmdInterpreter(Cmd):
    # We use this variable at Breakpoint #1.
    # We use this in order to allow Jarvis say "Hi", only at the first
    # interaction.

    # This can be used to store user specific data

    def __init__(self, first_reaction_text, prompt, first_reaction=True, enable_voice=False):
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

        self.actions = ("ask",
                        "calculate",
                        "cancel",
                        {"check": ("ram", "weather", "time", "forecast")},
                        "chuck",
                        "clear",
                        "clock",
                        "cricket",
                        {"decrease": ("volume",)},
                        "dictionary",
                        "directions",
                        {"disable": ("sound",)},
                        {"display": ("pics",)},
                        {"enable": ("sound",)},
                        "evaluate",
                        "exit",
                        "file_organise",
                        "fb",
                        "goodbye",
                        "hackathon",
                        "help",
                        {"hotspot": ("start", "stop")},
                        "how_are_you",
                        {"increase": ("volume",)},
                        "lyrics",
                        "match",
                        {"movie": ("cast", "director", "plot", "producer", "rating", "year",)},
                        "movies",
                        "music",
                        "mute",
                        "near",
                        "news",
                        {"open": ("camera",)},
                        "os",
                        "pinpoint",
                        "play",
                        "q",
                        "quit",
                        "quote",
                        "reboot",
                        "remind",
                        "say",
                        {"screen": ("off",)},
                        "shutdown",
                        "todo",
                        {"tell": ("joke",)},
                        "translate",
                        {"twitter": ("login", "tweet")},
                        "umbrella",
                        {"update": ("location", "system")},
                        "weather",
                        {"wiki": ("search", "summary", "content")}
                        )

        self.fixed_responses = {"what time is it": "clock",
                                "where am i": "pinpoint",
                                "how are you": "how_are_you"
                                }

        self.speech = voice.Voice()

    def close(self):
        """Closing Jarvis."""
        reminder_quit()
        print_say("Goodbye, see you later!", self, Fore.RED)
        exit()

    def completedefault(self, text, line, begidx, endidx):
        """Default completion"""
        return [i for i in self.actions if i.startswith(text)]

    def error(self):
        """Jarvis let you know if an error has occurred."""
        print_say("I could not identify your command...", self, Fore.RED)

    def get_completions(self, command, text):
        """Returns a list with the completions of a command."""
        dict_target = (item for item in self.actions
                       if type(item) == dict and command in item).next()  # next() will return the first match
        completions_list = dict_target[command]
        return [i for i in completions_list if i.startswith(text)]

    def interrupt_handler(self, signal, frame):
        """Closes Jarvis on SIGINT signal. (Ctrl-C)"""
        self.close()

    def do_ask(self, s):
        """Start chating with Jarvis"""
        if six.PY2:
            chat.main(self)
        else:
            print_say("Faeture currently not available in Python 3", self, Fore.RED)

    def help_ask(self):
        """Prints help about ask command."""
        print_say("Start chating with Jarvis", self)

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

    def do_cancel(self, s):
        """Cancel an active shutdown."""
        # TODO en el precmd creo que puedo hacerlo y asi no me hace falta para todos
        if "shutdown" in s:
            cancel_shutdown()

    def help_cancel(self):
        """Prints help about cancel command."""
        print_say("shutdown: Cancel an active shutdown.", self)
        # add here more prints

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

    def do_chuck(self, s):
        """Tell a joke about Chuck Norris"""
        chuck.main(self)

    def help_chuck(self):
        """Print info about Chuck command"""
        print_say("Tell a joke about Chuck Norris", self)

    def do_clear(self, s=None):
        """Clear terminal screen. """
        clear_scr()

    def help_clear(self):
        """Help:Clear terminal screen"""
        print_say("Clears terminal", self)

    def do_clock(self, s):
        """Gives information about time."""
        print_say(ctime(), self, Fore.BLUE)

    def help_clock(self):
        """Prints help about clock command."""
        print_say("Gives information about time.", self)

    def do_cricket(self, s=None):
        """Jarvis will show current matches and their score for you"""
        try:
            score(self)
        except ConnectionError:
            print(CONNECTION_ERROR_MSG)

    def help_cricket(self):
        """cricket package for Jarvis"""
        print_say("Enter cricket and follow the instructions", self)

    def do_decrease(self, s):
        """Decreases you speakers' sound."""
        # TODO si solo ponemos decrease que pase algo
        if s == "volume":
            if IS_MACOS:
                system(
                    'osascript -e "set volume output volume '
                    '(output volume of (get volume settings) - 10) --100%"'
                )
            else:
                system("pactl -- set-sink-volume 0 -10%")

    def help_decrease(self):
        """Print help about decrease command."""
        print_say("volume: Decreases you speaker's sound.", self)

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

    def do_evaluate(self, s):
        """Jarvis will get your calculations done!"""
        tempt = s.replace(" ", "")
        if len(tempt) > 1:
            evaluator.calc(tempt, self)
        else:
            print_say("Error: Not in correct format", self, Fore.RED)

    def help_evaluate(self):
        """Print help about evaluate command."""
        print_say("Jarvis will get your calculations done!", self)
        print_say("-- Example:", self)
        print_say("\tevaluate 3 + 5", self)

    def do_exit(self, s=None):
        """Closing Jarvis."""
        self.close()

    def help_exit(self):
        """Closing Jarvis."""
        print_say("Close Jarvis", self)

    def do_file_organise(self, s=None):
        """Jarvis will organise the given folder and group the files"""
        file_manage(self)

    def help_file_organise(self):
        """Help for file organise"""
        print_say("Type file_organise and follow instructions", self)
        print_say("It organises selected folder based on extension", self)

    def do_fb(self, s=None):
        """Jarvis will login into your facebook account either by prompting id-password or by using previously saved"""
        try:
            fb_login(self)
        except ConnectionError:
            print(CONNECTION_ERROR_MSG)

    def help_fb(self):
        """Help for fb"""
        print_say("type fb and follow instructions", self)

    def do_goodbye(self, s=None):
        """Closing Jarvis."""
        self.close()

    def help_goodbye(self):
        """Closing Jarvis."""
        print_say("Close Jarvis", self)

    def do_hackathon(self, s=None):
        """Find upcoming hackathons from hackerearth"""
        find_hackathon(self)

    def help_hackathon(self):
        """Prints help about hackathon command."""
        print_say("Find upcoming hackathons from hackerearth", self)

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

    def do_increase(self, s):
        """Increases you speakers' sound."""
        if s == "volume":
            if IS_MACOS:
                system(
                    'osascript -e "set volume output volume '
                    '(output volume of (get volume settings) + 10) --100%"'
                )
            else:
                system("pactl -- set-sink-volume 0 +3%")

    def help_increase(self):
        """Print help about increase command."""
        print_say("volume: Increases your speaker's sound.", self)

    def complete_increase(self, text, line, begidx, endidx):
        """Completions for increase command"""
        return self.get_completions("increase", text)

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
        if six.PY2:
            file_name = raw_input(Fore.RED + "Enter file name?:\n" + Fore.RESET)
            pattern = raw_input(Fore.GREEN + "Enter string:\n" + Fore.RESET)
        else:
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
        if six.PY2:
            movie_name = raw_input(
                Fore.RED + "What do you want to watch?\n" + Fore.RESET)
        else:
            movie_name = input(
                Fore.RED + "What do you want to watch?\n" + Fore.RESET)
        system("ims " + movie_name)

    @unsupported(platform=MACOS)
    def help_movies(self):
        """Print help about movies command."""
        print_say("Jarvis will find a good movie for you", self)

    @unsupported(platform=MACOS)
    def do_music(self, s):
        """Jarvis will find you a good song to relax!"""
        play(s)

    @unsupported(platform=MACOS)
    def help_music(self):
        """Print help about music command."""
        print_say("Jarvis will find you the song you want", self)
        print_say("-- Example:", self)
        print_say("\tmusic wonderful tonight", self)

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

    def do_os(self, s):
        """Displays information about your operating system."""
        print_say('[!] Operating System Information', self, Fore.BLUE)
        print_say('[*] ' + sys(), self, Fore.GREEN)
        print_say('[*] ' + release(), self, Fore.GREEN)
        print_say('[*] ' + dist()[0], self, Fore.GREEN)
        for _ in architecture():
            print_say('[*] ' + _, self, Fore.GREEN)

    def help_os(self):
        """Displays information about your operating system."""
        print_say("Displays information about your operating system.", self)

    def do_pinpoint(self, s):
        """Jarvis will pinpoint your location."""
        try:
            mapps.locate_me()
        except ConnectionError:
            print(CONNECTION_ERROR_MSG)

    def help_pinpoint(self):
        """Print help about pinpoint command."""
        print_say("Jarvis will pinpoint your location.", self)

    @unsupported(platform=MACOS)
    def do_play(self, s):
        """Jarvis will find you a good song to relax!"""
        play(s)

    @unsupported(platform=MACOS)
    def help_play(self):
        """Print help about play command."""
        print_say("Jarvis will find you the song you want", self)
        print_say("-- Example:", self)
        print_say("\tplay eye of the tiger", self)

    def do_q(self, s=None):
        """Closing Jarvis"""
        self.close()

    def help_q(self):
        """Closing Jarvis"""
        print_say("Closing Jarvis!!", self)

    def do_quit(self, s=None):
        """Closing Jarvis."""
        self.close()

    def help_quit(self):
        """Closing Jarvis."""
        print_say("Close Jarvis", self)

    def do_quote(self, s=None):
        """Show quote of the day"""
        show_quote(self)

    def help_quote(self):
        """Help for quote"""
        print_say("quote prints quote for the day for you", self)

    def do_reboot(self, s):
        """Reboot the system."""
        reboot_system()

    def help_reboot(self):
        """Print help about reboot command."""
        print_say("Reboot the system.", self)

    def do_remind(self, data):
        """Handles reminders"""
        reminder_handler(data)

    def help_remind(self):
        """Print help about remind command."""
        print_say("Handles reminders", self)
        print_say("add: adds a reminder", self)
        print_say("remove: removes a reminder", self)
        print_say("list: lists all reminders", self)
        print_say("clear: clears all reminders", self)
        print_say("-- Examples:", self)
        print_say("\tremind add 14:25 buy tomatoes", self)
        print_say("\tremind add 14:26 buy potatoes too", self)
        print_say("\tremind remove buy potatoes too", self)
        print_say("\tremind list", self)
        print_say("\tremind clear", self)

    def do_say(self, s):
        """Reads what is typed."""
        voice_state = self.enable_voice
        self.enable_voice = True
        self.speech.text_to_speech(s)
        self.enable_voice = voice_state

    def help_say(self):
        """Prints help text from say command."""
        print_say("Reads what is typed.")

    def do_screen(self, s):
        """Turns off the screen instantly"""
        if "off" in s:
            turn_off_screen()

    def help_screen(self):
        """Print help about screen command."""
        print_say("Turns off the screen instantly", self)
        print_say("-- Example:", self)
        print_say("screen off", self)

    def complete_screen(self, text, line, begidx, endidx):
        """Completions for screen command"""
        return self.get_completions("screen", text)

    def do_shutdown(self, s):
        """Shutdown the system."""
        shutdown_system()

    def help_shutdown(self):
        """Print help about shutdown command."""
        print_say("Shutdown the system.", self)

    def do_tell(self, s):
        """Tell a joke about Chuck Norris"""
        chuck.main(self)

    def help_tell(self):
        """Print info about tell command"""
        print_say("Tell a joke about Chuck Norris", self)

    def do_todo(self, data):
        """Create your personal TODO list!"""
        todoHandler(data)

    def help_todo(self):
        """Print help about todo command."""
        print_say("Create your personal TODO list!", self)
        print("Supported Commands: todo <command>")
        print(
            "\tadd [<index>] <todo - comment>, add comment <index> <comment>, add due <index> <time>")
        print("\tremove <index>")
        print("\tcomplete <index> [<completion>]")
        print("\tpriority <index> [<level>]")
        print("\tlist")

    def do_translate(self, s):
        """Translates text from one language (source) to another(destination)"""
        translate.main(self)

    def help_translate(self):
        """Print help for translate function"""
        print_say("translates from one language to another.", self)

    def do_twitter(self, s):
        """Jarvis will login into your facebook account either by prompting id-password or by using previously saved"""
        if "login" in s:
            try:
                driver = twitter_login(self)
                twitter_end(self, driver)
            except ConnectionError:
                print(CONNECTION_ERROR_MSG)
        elif "tweet" in s:
            try:
                driver = twitter_tweet(self)
                twitter_end(self, driver)
            except ConnectionError:
                print(CONNECTION_ERROR_MSG)

    def help_twitter(self):
        """help for twitter"""
        print_say("enter twitter and follow the instructions", self)

    def do_umbrella(self, s):
        """If you're leaving your place, Jarvis will inform you if you might need an umbrella or not"""
        s = 'umbrella'
        try:
            weather_pinpoint.main(MEMORY, self, s)
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
            location = MEMORY.get_data('city')
            loc_str = str(location)
            print_say("Your current location is set to " + loc_str, self)
            print_say("What is your new location?", self)
            if six.PY2:
                i = raw_input()
            else:
                i = input()
            MEMORY.update_data('city', i)
            MEMORY.save()
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
            weather_pinpoint.main(MEMORY, self, s)
        except ConnectionError:
            print(CONNECTION_ERROR_MSG)

    def help_weather(self):
        """Prints help about weather command."""
        print_say(
            "Get information about today's weather in your current location.", self)

    def do_wiki(self, s):
        """Jarvis will get wiki details for you"""
        k = s.split(' ', 1)
        data = None
        if k[0] == "search":
            data = wiki.search(" ".join(k[1:]))
        elif k[0] == "summary":
            data = wiki.summary(" ".join(k[1:]))
        elif k[0] == "content":
            data = wiki.content(" ".join(k[1:]))

        if isinstance(data, list):
            print("\nDid you mean one of these pages?\n")
            for d in range(len(data)):
                print(str(d + 1) + ": " + data[d])
        else:
            print("\n" + data)

    def help_wiki(self):
        """Help for wiki"""
        print_say("Jarvis has now wiki feature", self)
        print_say("enter wiki search for searching related topics", self)
        print_say("enter wiki summary for getting summary of the topic", self)
        print_say("wiki content for full page article of topic", self)

    def do_mute(self, s):
        """Silences your speaker's sound."""
        if IS_MACOS:
            pass
        else:
            system("pactl -- set-sink-mute 0 toggle")

    def help_mute(self):
        """Print help about mute command."""
        print_say("mute: Silences your speaker's sound.", self)
