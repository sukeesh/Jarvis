from os import system
from cmd import Cmd
import signal
from platform import system as sys
from platform import architecture, release, dist
from time import ctime
from colorama import Fore
from utilities import voice
from packages.music import play
from packages.todo import todoHandler
from packages.reminder import reminderHandler, reminderQuit
from packages import mapps, picshow, evaluator
from packages import chat, directions_to, near_me, weather_pinpoint, chuck
from packages.memory.memory import Memory
from packages.shutdown import shutdown_system, cancelShutdown, reboot_system
from packages.systemOptions import turn_off_screen, update_system
from packages.news import News

MEMORY = Memory()


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
        signal.signal(signal.SIGINT, self.interrupt_handler)  # Register do_quit() function to SIGINT signal (Ctrl-C)

        self.actions = ("ask",
                        "chat",
                        {"check": ("ram",)},
                        "chuck",
                        {"decrease": ("volume",)},
                        "directions",
                        {"disable": ("sound",)},
                        {"enable": ("sound",)},
                        "error",
                        "evaluate",
                        "exit",
                        "goodbye",
                        "help",
                        {"hotspot": ("start", "stop")},
                        {"increase": ("volume",)},
                        "match",
                        "movies",
                        "music",
                        "near",
                        "news",
                        {"open": ("camera",)},
                        "play",
                        "pinpoint",
                        "os",
                        "quit",
                        "remind",
                        "say",
                        {"screen": ("off",)},
                        {"display": ("pics",)},
                        "shutdown",
                        "reboot",
                        "todo",
                        {"update": ("location", "system")},
                        "weather",
                        )

        self.fixed_responses = {"what time is it": "clock",
                                "where am i": "pinpoint",
                                "how are you": "how_are_you"
                                }

        self.speech = voice.Voice()

    def completedefault(self, text, line, begidx, endidx):
        """Default completion"""
        return [i for i in self.actions if i.startswith(text)]

    def do_check(self, s):
        """Checks your system's RAM stats."""
        # if s == "ram":
        if "ram" in s:
            system("free -lm")

    def help_check(self):
        """Prints check command help."""
        print("ram: checks your system's RAM stats.")
        # add here more prints

    def get_completions(self, command, text):
        """Returns a list with the completions of a command."""
        dict_target = (item for item in self.actions
                       if type(item) == dict and command in item).next()  # next() will return the first match
        completions_list = dict_target[command]
        return [i for i in completions_list if i.startswith(text)]

    def complete_check(self, text, line, begidx, endidx):
        """Completions for check command"""
        return self.get_completions("check", text)

    def do_say(self, s):
        """Reads what is typed."""
        voice_state = self.enable_voice
        self.enable_voice = True
        self.speech.text_to_speech(s)
        self.enable_voice = voice_state

    def help_say(self):
        """Prints help text from say command."""
        print("Reads what is typed.")

    def interrupt_handler(self, signal, frame):
        """Closes Jarvis on SIGINT signal. (Crtl-C)"""
        self.close()

    def close(self):
        """Closing Jarvis."""
        reminderQuit()
        if self.enable_voice:
            self.speech.text_to_speech("Goodbye, see you later")
        print(Fore.RED + "Goodbye, see you later!" + Fore.RESET)
        exit()

    def do_exit(self, s=None):
        """Closing Jarvis."""
        self.close()

    def do_goodbye(self, s=None):
        """Closing Jarvis."""
        self.close()

    def do_quit(self, s=None):
        """Closing Jarvis."""
        self.close()

    def help_exit(self):
        """Closing Jarvis."""
        print("Close Jarvis")

    def help_goodbye(self):
        """Closing Jarvis."""
        print("Close Jarvis")

    def help_quit(self):
        """Closing Jarvis."""
        print("Close Jarvis")

    def do_ask(self, s):
        """Start chating with Jarvis"""
        chat.main()

    def help_ask(self):
        """Prints help about ask command."""
        print("Start chating with Jarvis")

    def do_clock(self, s):
        """Gives information about time."""
        print(Fore.BLUE + ctime() + Fore.RESET)

    def help_clock(self):
        """Prints help about clock command."""
        print("Gives information about time.")

    def do_decrease(self, s):
        """Decreases you speakers' sound."""
        # TODO si solo ponemos decrease que pase algo
        if s == "volume":
            system("pactl -- set-sink-volume 0 -10%")

    def help_decrease(self):
        """Print help about decrease command."""
        print("volume: Decreases you speaker's sound.")

    def complete_decrease(self, text, line, begidx, endidx):
        """Completions for decrease command"""
        return self.get_completions("decrease", text)

    def do_increase(self, s):
        """Increases you speakers' sound."""
        if s == "volume":
            system("pactl -- set-sink-volume 0 +3%")

    def help_increase(self):
        """Print help about increase command."""
        print("volume: Increases your speaker's sound.")

    def complete_increase(self, text, line, begidx, endidx):
        """Completions for increase command"""
        return self.get_completions("increase", text)

    def do_directions(self, data):
        """Get directions about a destination you are interested to."""
        directions_to.main(data)

    def help_directions(self):
        """Prints help about directions command"""
        print("Get directions about a destination you are interested to.")

    def do_display(self, s):
        """Displays photos."""
        if "pics" in s:
            s = s.replace("pics", "").strip()
            picshow.showpics(s)

    def help_display(self):
        """Prints help about display command"""
        print("Displays photos.")

    def complete_display(self, text, line, begidx, endidx):
        """Completions for display command"""
        return self.get_completions("display", text)

    def do_cancel(self, s):
        """Cancel an active shutdown."""
        # TODO en el precmd creo que puedo hacerlo y asi no me hace falta para todos
        if "shutdown" in s:
            cancelShutdown()

    def help_cancel(self):
        """Prints help about cancel command."""
        print("shutdown: Cancel an active shutdown.")
        # add here more prints

    def do_shutdown(self, s):
        """Shutdown the system."""
        shutdown_system()

    def help_shutdown(self):
        """Print help about shutdown command."""
        print("Shutdown the system.")

    def do_reboot(self, s):
        """Reboot the system."""
        reboot_system()

    def help_reboot(self):
        """Print help about reboot command."""
        print("Reboot the system.")

    def error(self):
        """Jarvis let you know if an error has occurred."""
        if self.enable_voice:
            self.speech.text_to_speech("I could not identify your command")
        print(Fore.RED + "I could not identify your command..." + Fore.RESET)

    def do_evaluate(self, s):
        """Jarvis will get your calculations done!"""
        tempt = s.split(" ", 1) or ""
        if len(tempt) > 1:
            evaluator.calc(tempt[1])
        else:
            print(Fore.RED + "Error: Not in correct format" + Fore.RESET)

    def help_evaluate(self):
        """Print help about evaluate command."""
        print("Jarvis will get your calculations done!")

    def do_hotspot(self, s):
        """Jarvis will set up your own hotspot."""
        if "start" in s:
            system("sudo ap-hotspot start")
        elif "stop" in s:
            system("sudo ap-hotspot stop")

    def help_hotspot(self):
        """Print help about hotspot commando."""
        print("start: Jarvis will set up your own hotspot.")
        print("stop: Jarvis will stop your hotspot.")

    def complete_hotspot(self, text, line, begidx, endidx):
        """Completions for enable command"""
        return self.get_completions("hotspot", text)

    def do_movies(self, s):
        """Jarvis will find a good movie for you."""
        try:
            movie_name = raw_input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)
        except:
            movie_name = input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)
        system("ims " + movie_name)

    def help_movies(self):
        """Print help about movies command."""
        print("Jarvis will find a good movie for you")

    def do_music(self, s):
        """Jarvis will find you a good song to relax!"""
        play(s)

    def help_music(self):
        """Print help about music command."""
        print("Jarvis will find you a good song to relax")

    def do_play(self, s):
        """Jarvis will find you a good song to relax!"""
        play(s)

    def help_play(self):
        """Print help about play command."""
        print("Jarvis will find you a good song to relax")

    def do_near(self, data):
        """Jarvis can find what is near you!"""
        near_me.main(data)

    def help_near(self, s):
        """Print help about near command."""
        print("Jarvis can find what is near you!")

    def do_news(self, s):
        """Time to get an update about the local news."""
        if s == "quick":
            try:
                n = News()
                n.quick_news()
            except:
                print Fore.RED + "I couldn't find news" + Fore.RESET
        else:
            try:
                n = News()
                n.news()
            except:
                print Fore.RED + "I couldn't find news" + Fore.RESET

    def help_news(self):
        """Print help about news command."""
        print("Time to get an update about the local news.")

    def do_open(self, s):
        """Jarvis will open the camera for you."""
        if "camera" in s:
            print "Opening Cheese ...... "
            system("cheese")

    def help_open(self):
        """Print help about open command."""
        print("camera: Jarvis will open the camera for you.")

    def complete_open(self, text, line, begidx, endidx):
        """Completions for open command"""
        return self.get_completions("open", text)

    def do_pinpoint(self, s):
        """Jarvis will pinpoint your location."""
        mapps.locateme()

    def help_pinpoint(self):
        """Print help about pinpoint command."""
        print("Jarvis will pinpoint your location.")

    def do_remind(self, data):
        """Handles reminders"""
        reminderHandler(data)

    def help_remind(self, data):
        """Print help about remind command."""
        print("Handles reminders")

    def do_match(self, s):
        """Matches patterns in a string by using regex."""
        try:
            file_name = raw_input(Fore.RED + "Enter file name?:\n" + Fore.RESET)
            stringg = raw_input(Fore.GREEN + "Enter string:\n" + Fore.RESET)
        except:
            file_name = input(Fore.RED + "Enter file name?:\n" + Fore.RESET)
            stringg = input(Fore.GREEN + "Enter string:\n" + Fore.RESET)
        system("grep '" + stringg + "' " + file_name)

    def help_match(self):
        """Prints help about match command"""
        print("Matches patterns in a string by using regex.")

    def do_todo(self, data):
        """Create your personal TODO list!"""
        todoHandler(data)

    def help_todo(self):
        """Print help about todo command."""
        print("Create your personal TODO list!")
        print("Supported Commands: todo <command>")
        print("\tadd [<index>] <todo - comment>, add comment <index> <comment>, add due <index> <time>")
        print("\tremove <index>")
        print("\tcomplete <index> [<completion>]")
        print("\tpriority <index> [<level>]")
        print("\tlist")

    def do_screen(self, s):
        """Turns off the screen instantly"""
        if "off" in s:
            turn_off_screen()

    def help_screen(self, s):
        """Print help about screen command."""
        print("Turns off the screen instantly")

    def complete_screen(self, text, line, begidx, endidx):
        """Completions for screen command"""
        return self.get_completions("screen", text)

    def do_os(self, s):
        """Displays information about your operating system."""
        print Fore.BLUE + '[!] Operating System Information' + Fore.RESET
        print Fore.GREEN + '[*] ' + sys() + Fore.RESET
        print Fore.GREEN + '[*] ' + release() + Fore.RESET
        print Fore.GREEN + '[*] ' + dist()[0] + Fore.RESET
        for _ in architecture():
            print Fore.GREEN + '[*] ' + _ + Fore.RESET

    def help_os(self):
        """Displays information about your operating system."""
        print("Displays information about your operating system.")

    def do_enable(self, s):
        """Let Jarvis use his voice."""
        if "sound" in s:
            self.enable_voice = True

    def help_enable(self):
        """Displays help about enable command"""
        print("Let Jarvis use his voice.")

    def complete_enable(self, text, line, begidx, endidx):
        """Completions for enable command"""
        return self.get_completions("enable", text)

    def do_disable(self, s):
        """Deny Jarvis to use his voice."""
        if "sound" in s:
            self.enable_voice = False

    def help_disable(self):
        """Displays help about disable command"""
        print("Deny Jarvis to use his voice.")

    def complete_disable(self, text, line, begidx, endidx):
        """Completions for check command"""
        return self.get_completions("disable", text)

    def do_update(self, s):
        """Updates location or system."""
        if "location" in s:
            location = MEMORY.get_data('city')
            loc_str = str(location)
            print("Your current location is set to " + loc_str)
            print("What is your new location?")
            try:
                i = raw_input()
            except:
                i = input()
            MEMORY.update_data('city', i)
            MEMORY.save()
        elif "system" in s:
            update_system()

    def complete_update(self, text, line, begidx, endidx):
        """Completions for update command"""
        return self.get_completions("update", text)

    def help_update(self):
        """Prints help about update command"""
        print("location: Updates location.")
        print("system: Updates system.")

    def do_weather(self, s):
        """Get information about today's weather."""
        weather_pinpoint.main(MEMORY)

    def help_weather(self):
        """Prints help about weather command."""
        print("Get information about today's weather.")

    def do_how_are_you(self, s):
        """Jarvis will inform you about his status."""
        if self.enable_voice:
            self.speech.text_to_speech("I am fine, thank you")
        print(Fore.BLUE + "I am fine, How about you" + Fore.RESET)

    def help_how_are_you(self, s):
        """Print info about how_are_you command"""
        print("Jarvis will inform you about his status.")

    def do_chuck(self, s):
        """Tell a joke about Chuck Norris"""
        chuck.main(self)

    def help_chuck(self):
        """Print info about Chuck command"""
        print("Tell a joke about Chuck Norris")
