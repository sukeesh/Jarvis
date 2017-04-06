from os import system
from cmd import Cmd
import requests
import signal
from platform import system as sys
from platform import architecture, release, dist
from time import ctime
from colorama import Fore
from utilities.GeneralUtilities import wordIndex
from utilities import voice
from packages.music import play
from packages.todo import todoHandler
from packages.reminder import reminderHandler, reminderQuit
from packages import newws, mapps, picshow, evaluator
from packages.aiml.brain import Brain
from packages.memory.memory import Memory
from packages.shutdown import shutdown_system, cancelShutdown, reboot_system

"""
    AUTHORS' SCOPE:
        We thought that the source code of Jarvis would
        be more organized if we treat Jarvis as Object.
        So we decided to create this Jarvis Class which
        implements the core functionality of Jarvis in a
        simpler way than the original __main__.py.
    HOW TO EXTEND JARVIS:
        If you would like to add extra functionality to
        Jarvis (for example new actions like "record" etc.)
        you only need to add this action to the action dict
        (look on __init__(self)) along with a apropriate
        function name. Then you need to implement this function
        as a local function on reactions() method.
    DETECTED ISSUES:
        * Furthermore, "near me" command is unable to find
        the actual location of our laptops.
"""

MEMORY = Memory()


class Jarvis(Cmd):
    # We use this variable at Breakpoint #1.
    # We use this in order to allow Jarvis say "Hi", only at the first interaction.
    first_reaction = True
    enable_voice = False
    first_reaction_text = ""
    first_reaction_text += Fore.BLUE + 'Jarvi\'s sound is by default disabled.' + Fore.RESET
    first_reaction_text += "\n"
    first_reaction_text += Fore.BLUE + 'In order to let Jarvis talk out loud type: '
    first_reaction_text += Fore.RESET + Fore.RED + 'enable sound' + Fore.RESET
    first_reaction_text += "\n"

    #This can be used to store user specific data

    def __init__(self, first_reaction_text=first_reaction_text):
        """
        This constructor contains a dictionary with Jarvis Actions (what Jarvis can do).
        In alphabetically order.
        """
        Cmd.__init__(self)
        self.prompt = Fore.RED + "~> Hi, what can i do for you?\n" + Fore.RESET
        self.first_reaction_text = first_reaction_text
        signal.signal(signal.SIGINT, self.interrupt_handler)  # Register do_quit() function to SIGINT signal (Ctrl-C)

        self.actions = ("ask jarvis",
                        "chat",
                        {"check": ("ram",)},
                        "decrease volume",
                        "directions",
                        "disable sound",
                        "enable sound",
                        "error",
                        "evaluate",
                        "exit",
                        "goodbye",
                        "help",
                        "hotspot start",
                        "hotspot stop",
                        "how are you",
                        "increase volume",
                        "movies",
                        "music",
                        "near",
                        "news",
                        "open camera",
                        "os",
                        "quit",
                        "remind",
                        "say",
                        "search for a string in file",
                        "show me pics of",
                        "shutdown -c",
                        "shutdown system",
                        "reboot system",
                        "todo",
                        "update location",
                        "weather",
                        "what time is it",
                        "where am i",
                        "what about chuck"
        )

        self.speech = voice.Voice()

    def default(self, data):
        """
        Jarvis let's you know if an error has occurred.
        """
        if self.enable_voice:
            self.speech.text_to_speech("I could not identify your command")
        print(Fore.RED + "I could not identify your command..." + Fore.RESET)

    def completedefault(self, text, line, begidx, endidx):
        return [i for i in self.actions if i.startswith(text)]

    def precmd(self, line):
        if len(line.split()) > 2:
            line = self.find_action(line)
        return line

    def postcmd(self, stop, line):
        """
        Hook that executes after every command.
        """
        if Jarvis.first_reaction:
            self.prompt = self.prompt = Fore.RED + "~> What can i do for you?\n" + Fore.RESET
            Jarvis.first_reaction = False
        if self.enable_voice:
            self.speech.text_to_speech("What can i do for you?\n")


    def do_check(self, s):
        """
        Checks your system's RAM stats.
        """
        s = s.lower()
        # if s == "ram":
        if "ram" in s:
            system("free -lm")

    def help_check(self):
        """
        Prints check command help.
        """
        print("ram: checks your system's RAM stats.")
        # add here more prints

    def complete_check(self, text, line, begidx, endidx):
        check_completions = ("ram",)  # add here more command completions to check
        return [i for i in check_completions if i.startswith(text)]

    def do_say(self, s):
        """
        Reads what is typed.
        """
        voice_state = self.enable_voice
        self.enable_voice = True
        self.speech.text_to_speech(s)
        self.enable_voice = voice_state

    def help_say(self):
        """
        Prints help text from say command.
        """
        print("Reads what is typed.")

    def interrupt_handler(self, signal, frame):
        """
        Closes Jarvis on SIGINT signal. (Crtl-C)
        """
        self.close()

    def close(self):
        """
        Closing Jarvis.
        """
        reminderQuit()
        if self.enable_voice:
            self.speech.text_to_speech("Goodbye, see you later")
        print(Fore.RED + "Goodbye, see you later!" + Fore.RESET)
        exit()

    def do_exit(self, s=None):
        """
        Closing Jarvis.
        """
        self.close()

    def do_goodbye(self, s=None):
        """
        Closing Jarvis.
        """
        self.close()

    def do_quit(self, s=None):
        """
        Closing Jarvis.
        """
        self.close()

    def help_exit(self):
        """
        Closing Jarvis.
        """
        print("Close Jarvis")

    def help_goodbye(self):
        """
        Closing Jarvis.
        """
        print("Close Jarvis")

    def help_quit(self):
        """
        Closing Jarvis.
        """
        print("Close Jarvis")

    def do_ask(self, s):
        brain = Brain()
        print(Fore.BLUE + "Ask me anything\n type 'leave' to stop" + Fore.RESET)
        stay = True

        while stay:
            try:
                text = str.upper(raw_input(Fore.RED + ">> " + Fore.RESET))
            except:
                text = str.upper(input(Fore.RED + ">> " + Fore.RESET))
            if text == "LEAVE":
                print("thanks for talking to me")
                stay = False
            else:
                print(brain.respond(text))

    def help_ask(self):
        """
        Prints help about ask command.
        """
        print("Ask something to Jarvis")

    def do_clock(self, s):
        """
        Gives information about time.
        """
        print(Fore.BLUE + ctime() + Fore.RESET)

    def help_clock(self):
        """
        Prints help about clock command.
        """
        print("Gives information about time.")

    def do_decrease(self, s):
        """
        Decreases you speakers' sound.
        """
        # TODO si solo ponemos decrease que pase algo
        s = s.lower()
        if s == "volume":
            system("pactl -- set-sink-volume 0 -10%")

    def help_decrease(self):
        """
        Print help about decrease command.
        """
        print("volume: Decreases you speaker's sound.")

    def complete_decrease(self, text, line, begidx, endidx):
        completions = ("volume",)  # add here more command completions to decrease
        return [i for i in completions if i.startswith(text)]

    def do_increase(self, s):
        """
        Increases you speakers' sound.
        """
        s = s.lower()
        if s == "volume":
            system("pactl -- set-sink-volume 0 +3%")

    def help_increase(self):
        """
        Print help about increase command.
        """
        print("volume: Increases your speaker's sound.")

    def complete_increase(self, text, line, begidx, endidx):
        completions = ("volume",)  # add here more command completions to increase
        return [i for i in completions if i.startswith(text)]

    def do_directions(self, data):
        # TODO no va
        """
        Get directions about a destination you are interested to.
        """
        wordList = data.split()
        to_index = wordIndex(data, "to")
        if " from " in data:
            from_index = wordIndex(data, "from")
            if from_index > to_index:
                toCity = " ".join(wordList[to_index + 1:from_index])
                fromCity = " ".join(wordList[from_index + 1:])
            else:
                fromCity = " ".join(wordList[from_index + 1:to_index])
                toCity = " ".join(wordList[to_index + 1:])
        else:
            toCity = " ".join(wordList[to_index + 1:])
            fromCity = 0
        mapps.directions(toCity, fromCity)

    def help_directions(self):
        """
        Prints help about directions command
        """
        print("Get directions about a destination you are interested to.")


    # # TODO seguir por aqui
    # def display_pics():
    #     """
    #     Displays photos.
    #     """
    #     picshow.showpics(data)
    #
    # def cancel_shutdown():
    #     """
    #     Cancel an active shutdown.
    #     """
    #     cancelShutdown()
    #
    def do_shutdown(self, s):
        """
        Shutdown the system.
        """
        shutdown_system()

    def help_shutdown(self):
        """
        Print help about shutdown command.
        """
        print("Shutdown the system.")

    def do_reboot(self, s):
        """
        Reboot the system.
        """
        reboot_system()

    def help_reboot(self):
        """
        Print help about reboot command.
        """
        print("Reboot the system.")

    def error(self):
        """
        Jarvis let you know if an error has occurred.
        """
        if self.enable_voice:
            self.speech.text_to_speech("I could not identify your command")
        print(Fore.RED + "I could not identify your command..." + Fore.RESET)

    def do_evaluate(self, s):
        """
        Jarvis will get your calculations done!
        """
        tempt = s.split(" ", 1) or ""
        if len(tempt) > 1:
            evaluator.calc(tempt[1])
        else:
            print(Fore.RED + "Error: Not in correct format" + Fore.RESET)

    def help_evaluate(self):
        """
        Print help about evaluate command.
        """
        print("Jarvis will get your calculations done!")
    #
    # def hotspot_start():
    #     """
    #     Jarvis will set up your own hotspot.
    #     """
    #     system("sudo ap-hotspot start")
    #
    # def hotspot_stop():
    #     """
    #     Jarvis will turn of the hotspot.
    #     """
    #     system("sudo ap-hotspot stop")
    #
    # def how_are_you():
    #     """
    #     Jarvis will inform you about his status.
    #     """
    #     if self.enable_voice:
    #         self.speech.text_to_speech("I am fine, thank you")
    #     print(Fore.BLUE + "I am fine, How about you" + Fore.RESET)
    #
    def do_movies(self, s):
        """
        Jarvis will find a good movie for you.
        """
        try:
            movie_name = raw_input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)
        except:
            movie_name = input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)
        system("ims " + movie_name)

    def help_movies(self):
        """
        Print help about movies command.
        """
        print("Jarvis will find a good movie for you")

    def do_music(self, s):
        """
        Jarvis will find you a good song to relax!
        """
        play(s)

    def help_music(self):
        """
        Print help about music command.
        """
        print("Jarvis will find you a good song to relax")

    def do_near(self, data):
        """
        Jarvis can find what is near you!
        """
        wordList = data.split()
        things = " ".join(wordList[0:wordIndex(data, "near")])
        if " me" in data:
            city = 0
        else:
            wordList = data.split()
            city = " ".join(wordList[wordIndex(data, "near") + 1:])
            print city
        mapps.searchNear(things, city)

    def help_near(self, s):
        """
        Print help about near command.
        """
        print("Jarvis can find what is near you!")

    def do_news(self, s):
        """
        Time to get an update about the local news.
        """
        try:
            newws.show_news()
        except:
            print Fore.RED + "I couldn't find news" + Fore.RESET

    def help_news(self):
        """
        Print help about news command.
        """
        print("Time to get an update about the local news.")
    #
    #
    # def open_camera():
    #     """
    #     Jarvis will open the camera for you.
    #     """
    #     print "Opening Cheese ...... "
    #     system("cheese")
    #
    def do_pinpoint(self, s):
        """
        Jarvis will pinpoint your location.
        """
        mapps.locateme()

    def help_pinpoint(self):
        """
        Print help about pinpoint command.
        """
        print("Jarvis will pinpoint your location.")

    def do_remind(self, data):
        """
        Handles reminders
        """
        reminderHandler(data.replace("remind", "", 1))

    def help_remind(self, data):
        """
        Print help about remind command.
        """
        print("Handles reminders")
    #
    # def string_pattern():
    #     """
    #     Matches patterns in a string by using regex.
    #     """
    #     try:
    #         file_name = raw_input(Fore.RED + "Enter file name?:\n" + Fore.RESET)
    #         stringg = raw_input(Fore.GREEN + "Enter string:\n" + Fore.RESET)
    #     except:
    #         file_name = input(Fore.RED + "Enter file name?:\n" + Fore.RESET)
    #         stringg = input(Fore.GREEN + "Enter string:\n" + Fore.RESET)
    #     system("grep '" + stringg + "' " + file_name)
    #
    def do_todo(self, data):
        """
        Create your personal TODO list!
        """
        # TODO data replace no longer necesary?
        todoHandler(data.replace("todo", "", 1))

    def help_todo(self):
        """
        Print help about help command.
        """
        print("Create your personal TODO list!")

    def do_os(self, s):
        """
        Displays information about your operating system.
        """
        print Fore.BLUE + '[!] Operating System Information' + Fore.RESET
        print Fore.GREEN + '[*] ' + sys() + Fore.RESET
        print Fore.GREEN + '[*] ' + release() + Fore.RESET
        print Fore.GREEN + '[*] ' + dist()[0] + Fore.RESET
        for _ in architecture():
            print Fore.GREEN + '[*] ' + _ + Fore.RESET

    def help_os(self):
        """
        Displays information about your operating system.
        """
        print("Displays information about your operating system.")
    #
    # def enable_sound():
    #     """
    #     Let Jarvis use his voice.
    #     """
    #     self.enable_voice = True
    #
    # def disable_sound():
    #     """
    #     Deny Jarvis to use his voice.
    #     """
    #     self.enable_voice = False
    #
    # def update_location():
    #     location = MEMORY.get_data('city')
    #     loc_str = str(location)
    #     print("Your current location is set to " + loc_str)
    #     print("What is your new location?")
    #     try:
    #         i = raw_input()
    #     except:
    #         i = input()
    #     MEMORY.update_data('city', i)
    #     MEMORY.save()
    #
    #

    def do_weather(self, s):
        """
        Get information about today's weather.
        """

        location = MEMORY.get_data('city') #Will return None if no value
        if location is None:
            loc = str(location)
            city = mapps.getLocation()['city']
            print(Fore.RED + "It appears you are in " + city + " Is this correct? (y/n)" + Fore.RESET)

            try:
                i = raw_input()
            except:
                i = input()
            if i == 'n' or i == 'no':
                print("Enter Name of city: ")
                try:
                    i = raw_input()
                except:
                    i = input()
                city = i

            mapps.weather(str(city))

            MEMORY.update_data('city', city)
            MEMORY.save()
        else:
            loc = str(location)
            city = mapps.getLocation()['city']
            if city != loc:
                print(Fore.RED + "It appears you are in " + city + ". But you set your location to " + loc + Fore.RESET)
                print(Fore.RED + "Do you want weather for " + city + " instead? (y/n)" + Fore.RESET)
                try:
                    i = raw_input()
                except:
                    i = input()
                if i == 'y' or i == 'yes':
                    try:
                        print(Fore.RED + "Would you like to set " + city + " as your new location? (y/n)" + Fore.RESET)
                        try:
                            i = raw_input()
                        except:
                            i = input()
                        if i == 'y' or i == 'yes':
                            MEMORY.update_data('city', city)
                            MEMORY.save()

                        mapps.weather(city)
                    except:
                        print(Fore.RED + "I couldn't locate you" + Fore.RESET)
                else:
                    try:
                        mapps.weather(loc)
                    except:
                        print(Fore.RED + "I couldn't locate you" + Fore.RESET)
            else:
                try:
                    mapps.weather(loc)
                except:
                    print(Fore.RED + "I couldn't locate you" + Fore.RESET)

    def help_weather(self):
        """
        Prints help about weather command.
        """
        print("Get information about today's weather.")
    #
    #
    # def what_about_chuck():
    #     try:
    #         req = requests.get("https://api.chucknorris.io/jokes/random")
    #         chuck_json = req.json()
    #
    #         chuck_fact = chuck_json["value"]
    #         if self.enable_voice:
    #             print(Fore.RED + chuck_fact + Fore.RESET)
    #             self.speech.text_to_speech(chuck_fact)
    #         else:
    #             print(Fore.RED + chuck_fact + Fore.RESET)
    #     except:
    #         if self.enable_voice:
    #             self.speech.text_to_speech("Looks like Chuck broke the Internet.")
    #         else:
    #             print(Fore.RED + "Looks like Chuck broke the Internet..." + Fore.RESET)
    #
    # locals()[key]()  # we are calling the proper function which satisfies the user's command.

    def speak(self):
        if self.enable_voice:
            self.speech.speak(self.first_reaction)


# a = (
#     "lol",
#     {"food": ("banana",)},
#     "z"
# )
#
# output = ""
# resto_frase = "banana"
# for item in a:
#     if type(item) is dict:
#         output = item.keys()[0]
#         for word in resto_frase.split():
#             print word
#             if word in item.values()[0]:
#                 output += " " + word

    def find_action(self, data):
        """
        This method gets the data and assigns it to an action
        """
        user_wish = "null"
        for key in self.actions:
            print key
            if type(key) is dict:
                # TODO como manejar casos como my ram
                # si el valor de la key es el nombre pues empezamos a crear el user wish poniendo como primer valor el
                # nombre
                # buscamos en el resto del text a ver si hay coincide con el contenido del dict
                print "is a dict"
            # if isinstance(dict, key):
            #     print "is a dict"
            elif key in data:
                print "lol"
                user_wish = key
        if user_wish in self.actions:
            return user_wish
        return "error"

    def executor(self):
        """
        This method is opening a terminal session with the user.
        We can say that it is the core function of this whole class
        and it joins all the function above to work together like a
        clockwork. (Terminates when the user send the "exit", "quit"
        or "goodbye command")
        :return: Nothing to return.
        """
        self.speak()
        self.cmdloop(self.first_reaction_text)

