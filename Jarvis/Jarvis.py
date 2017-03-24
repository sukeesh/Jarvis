from os import system
import requests
from platform import system as sys
from platform import architecture, release, dist
from time import ctime
from colorama import Fore
from utilities.GeneralUtilities import wordIndex
from utilities import voice
from packages.music import play
from packages.todo import todoHandler
from packages import newws, mapps, picshow, evaluator
from packages.aiml.brain import Brain

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

class Jarvis:
    # We use this variable at Breakpoint #1.
    # We use this in order to allow Jarvis say "Hi", only at the first interaction.
    first_reaction = True
    enable_voice = False

    def __init__(self):
        """
        This constructor contains a dictionary with Jarvis Actions (what Jarvis can do).
        In alphabetically order.
        """
        self.actions = {"about os": "os_detection",
                        "ask jarvis": "ask_jarvis",
                        "check ram": "check_ram",
                        "decrease volume": "decrease_volume",
                        "directions": "directions",           # Doesn't check if 'to' exist
                        "disable sound": "disable_sound",
                        "enable sound": "enable_sound",
                        "error": "error",
                        "evaluate": "evaluate",
                        "exit": "quit",
                        "goodbye": "quit",
                        "help": "help_jarvis",
                        "hotspot start": "hotspot_start",
                        "hotspot stop": "hotspot_stop",
                        "how are you?": "how_are_you",
                        "increase volume": "increase_volume",
                        "movies": "movies",
                        "music": "music",
                        "near": "near",
                        "news": "news",
                        "open camera": "open_camera",
                        "quit": "quit",
                        "search for a string in file": "string_pattern",
                        "show me pics of": "display_pics",
                        "todo": "todo",
                        "weather": "weather",
                        "what time is it": "clock",
                        "where am i": "pinpoint",
                        "what about chuck": "what_about_chuck",
                        }
        self.speech = voice.Voice()

    #@staticmethod
    def reactions(self, key, data):
        """
        This function contains local functions which are implementing
        Jarvis' actions. In alphabetically order.
        :param key: the action which corresponds to a local function
                    eg. key = (How are you) (according to actions dictionary)
                    corresponds to how_are_you() function.
                Data: the data which corresponds to an extra input needed
                    eg. music method needs a song name. (music closer)
        :return: This method does not return any objects.
        """

        def ask_jarvis():
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


        def check_ram():
            """
            Checks your system's RAM stats.
            """
            system("free -lm")

        def clock():
            """
            Gives information about time.
            """
            print(Fore.BLUE + ctime() + Fore.RESET)

        def decrease_volume():
            """
            Decreases you speakers' sound.
            """
            system("pactl -- set-sink-volume 0 -10%")

        def directions():
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

        def disable_sound():
            self.enable_voice = False

        def display_pics():
            """
            Displays photos.
            """
            picshow.showpics(data)

        def enable_sound():
            self.enable_voice = True

        def error():
            """
            Jarvis let you know if an error has occurred.
            """
            if self.enable_voice:
                self.speech.text_to_speech("I could not identify your command")
            print(Fore.RED + "I could not identify your command..." + Fore.RESET)

        def evaluate():
            """
            Jarvis will get your calculations done!
            """
            tempt = data.split(" ", 1) or ""
            if len(tempt) > 1:
                evaluator.calc(tempt[1])
            else:
                print(Fore.RED + "Error : Not in correct format" + Fore.RESET)

        def help_jarvis():
            """
            This method displays help about Jarvis.
            :return: Nothing to return.
            """
            print Fore.BLUE + '>>> Usage: ' + Fore.RESET
            print Fore.BLUE + 'Type any of the following commands to interact with Jarvis.' + Fore.RESET
            print Fore.GREEN + '[*] Help: To see this message' + Fore.RESET
            print Fore.GREEN + '[*] How are you?: To react with Jarvis!' + Fore.RESET
            print Fore.GREEN + '[*] Open Camera: To open "cheese" program (camera).' + Fore.RESET
            print Fore.GREEN + '[*] What time is it: To check the time.' + Fore.RESET
            print Fore.GREEN + '[*] Where am i: To pinpoint your location.' + Fore.RESET
            print Fore.GREEN + '[*] Near me: To see nearby locations.' + Fore.RESET
            print Fore.GREEN + '[*] Music: To listen some good Music!' + Fore.RESET
            print Fore.GREEN + '[*] Increase Volume: To increase your system volume.' + Fore.RESET
            print Fore.GREEN + '[*] Decrease Volume: To decrease your system volume.' + Fore.RESET
            print Fore.GREEN + '[*] Hotspot Start: To set up your own hotspot.' + Fore.RESET
            print Fore.GREEN + '[*] Hotspot Stop: To stop your personal hotspot.' + Fore.RESET
            print Fore.GREEN + '[*] Search for a string in a file: Match patterns in a string using regex.' + Fore.RESET
            print Fore.GREEN + '[*] Check RAM: Detailed RAM usage.' + Fore.RESET
            print Fore.GREEN + '[*] Todo: An ordinary TODO list.' + Fore.RESET
            print Fore.GREEN + '[*] News: Get an update about the news!' + Fore.RESET
            print Fore.GREEN + '[*] Show me pics of: Displays the selected pics.' + Fore.RESET
            print Fore.GREEN + '[*] Evaluate: To get your calculations done!' + Fore.RESET
            print Fore.GREEN + '[*] Show me directions from: Get directions about your destination!' + Fore.RESET
            print Fore.GREEN + '[*] enable sound: Jarvis will start talking to you' + Fore.RESET
            print Fore.GREEN + '[*] disable sound: Jarvis will no longer talks out loud...' + Fore.RESET
            print Fore.GREEN + '[*] about os: Dispays detailed information about your operating system' + Fore.RESET
            print Fore.GREEN + '[*] quit: Close the session with Jarvis...' + Fore.RESET
            print Fore.GREEN + '[*] exit: Close the session with Jarvis...' + Fore.RESET
            print Fore.GREEN + '[*] Goodbye: Close the session with Jarvis...' + Fore.RESET

        def hotspot_start():
            """
            Jarvis will set up your own hotspot.
            """
            system("sudo ap-hotspot start")

        def hotspot_stop():
            """
            Jarvis will turn of the hotspot.
            """
            system("sudo ap-hotspot stop")

        def how_are_you():
            """
            Jarvis will inform you about his status.
            """
            if self.enable_voice:
                self.speech.text_to_speech("I am fine, thank you")
            print(Fore.BLUE + "I am fine, How about you" + Fore.RESET)

        def increase_volume():
            """
            Increases your speakers' volume.
            """
            system("pactl -- set-sink-volume 0 +3%")

        def movies():
            """
            Jarvis will find a good movie for you.
            """
            try:
                movie_name = raw_input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)
            except:
                movie_name = input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)
            system("ims " + movie_name)

        def music():
            """
            Jarvis will find you a good song to relax!
            """
            play(data)

        def near():
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

        def news():

            """
            Time to get an update about the local news.
            """
            try:
                newws.show_news()
            except:
                print Fore.RED + "I couldn't find news" + Fore.RESET


        def open_camera():
            """
            Jarvis will open the camera for you.
            """
            print "Opening Cheese ...... "
            system("cheese")

        def os_detection():
            """
            This method displays a detailed operating system
            information
            :return: Nothing to return.
            """
            print Fore.BLUE + '[!] Operating System Information' + Fore.RESET
            print Fore.GREEN + '[*] ' + sys() + Fore.RESET
            print Fore.GREEN + '[*] ' + release() + Fore.RESET
            print Fore.GREEN + '[*] ' + dist()[0] + Fore.RESET
            for _ in architecture():
                print Fore.GREEN + '[*] ' + _ + Fore.RESET

        def pinpoint():
            """
            Jarvis will pinpoint your location.
            """
            mapps.locateme()

        def quit():
            """
            Closing Jarvis.
            """
            if self.enable_voice:
                self.speech.text_to_speech("Goodbye, see you later")
            print(Fore.RED + "Goodbye, see you later!" + Fore.RESET)
            exit()

        def string_pattern():
            """
            Matches patterns in a string by using regex.
            """
            try:
                file_name = raw_input(Fore.RED + "Enter file name?:\n" + Fore.RESET)
                stringg = raw_input(Fore.GREEN + "Enter string:\n" + Fore.RESET)
            except:
                file_name = input(Fore.RED + "Enter file name?:\n" + Fore.RESET)
                stringg = input(Fore.GREEN + "Enter string:\n" + Fore.RESET)
            system("grep '" + stringg + "' " + file_name)

        def todo():
            """
            Create your personal TODO list!
            """
            todoHandler(data)


        def os_detection():
            """
            Displays information about your operating system.
            """
            print Fore.BLUE + '[!] Operating System Information' + Fore.RESET
            print Fore.GREEN + '[*] ' + sys() + Fore.RESET
            print Fore.GREEN + '[*] ' + release() + Fore.RESET
            print Fore.GREEN + '[*] ' + dist()[0] + Fore.RESET
            for _ in architecture():
                print Fore.GREEN + '[*] ' + _ + Fore.RESET

        def enable_sound():
            """
            Let Jarvis use his voice.
            """
            self.enable_voice = True

        def disable_sound():
            """
            Deny Jarvis to use his voice.
            """
            self.enable_voice = False

        def help_jarvis():
            """
            This method displays help about Jarvis.
            """
            print Fore.BLUE + '>>> Usage: ' + Fore.RESET
            print Fore.BLUE + 'Type any of the following commands to interact with Jarvis.' + Fore.RESET
            print Fore.GREEN + '[*] Help: To see this message' + Fore.RESET
            print Fore.GREEN + '[*] How are you?: To react with Jarvis!' + Fore.RESET
            print Fore.GREEN + '[*] Open Camera: To open "cheese" program (camera).' + Fore.RESET
            print Fore.GREEN + '[*] What time is it: To check the time.' + Fore.RESET
            print Fore.GREEN + '[*] Where am i: To pinpoint your location.' + Fore.RESET
            print Fore.GREEN + '[*] Near me: To see nearby locations.' + Fore.RESET
            print Fore.GREEN + '[*] Music: To listen some good Music!' + Fore.RESET
            print Fore.GREEN + '[*] Increase Volume: To increase your system volume.' + Fore.RESET
            print Fore.GREEN + '[*] Decrease Volume: To decrease your system volume.' + Fore.RESET
            print Fore.GREEN + '[*] Hotspot Start: To set up your own hotspot.' + Fore.RESET
            print Fore.GREEN + '[*] Hotspot Stop: To stop your personal hotspot.' + Fore.RESET
            print Fore.GREEN + '[*] Search for a string in a file: Match patterns in a string using regex.' + Fore.RESET
            print Fore.GREEN + '[*] Check RAM: Detailed RAM usage.' + Fore.RESET
            print Fore.GREEN + '[*] Todo: An ordinary TODO list.' + Fore.RESET
            print Fore.GREEN + '[*] News: Get an update about the news!' + Fore.RESET
            print Fore.GREEN + '[*] Show me pics of: Displays the selected pics.' + Fore.RESET
            print Fore.GREEN + '[*] Evaluate: To get your calculations done!' + Fore.RESET
            print Fore.GREEN + '[*] Show me directions from: Get directions about your destination!' + Fore.RESET
            print Fore.GREEN + '[*] enable sound: Jarvis will start talking to you' + Fore.RESET
            print Fore.GREEN + '[*] disable sound: Jarvis will no longer talks out loud...' + Fore.RESET
            print Fore.GREEN + '[*] about os: Dispays detailed information about your operating system' + Fore.RESET
            print Fore.GREEN + '[*] quit: Close the session with Jarvis...' + Fore.RESET
            print Fore.GREEN + '[*] exit: Close the session with Jarvis...' + Fore.RESET
            print Fore.GREEN + '[*] Goodbye: Close the session with Jarvis...' + Fore.RESET

        def weather():
            """
            Get information about today's weather.
            """
            try:
                mapps.weather()
            except:
                print(Fore.RED + "I couldn't locate you" + Fore.RESET)

        def what_about_chuck():
            try:
                req = requests.get("https://api.chucknorris.io/jokes/random")
                chuck_json = req.json()

                chuck_fact = chuck_json["value"]
                if self.enable_voice:
                    print(Fore.RED + chuck_fact + Fore.RESET)
                    self.speech.text_to_speech(chuck_fact)
                else:
                    print(Fore.RED + chuck_fact + Fore.RESET)
            except:
                if self.enable_voice:
                    self.speech.text_to_speech("Looks like Chuck broke the Internet.")
                else:
                    print(Fore.RED + "Looks like Chuck broke the Internet..." + Fore.RESET)

        locals()[key]()  # we are calling the proper function which satisfies the user's command.

    def user_input(self):
        """
        This method is responsible for getting the user's input.
        We are using first_reaction variable in order to prompt
        "Hi" only the first time we "meet" our user (in your first version
        whenever you asked for a command Jarvis where saying "Hi").
        :return: user_data, a variable containing the Jarvis' action
                 that user wants to execute.
        """
        # BREAKPOINT #1
        if self.first_reaction:
            self.speak()
            print Fore.BLUE + 'Jarvis\' is by default disabled.' + Fore.RESET
            print Fore.BLUE + 'In order to let Jarvis talk out loud type: ' +\
                  Fore.RESET + Fore.RED + 'enable sound' + Fore.RESET
            print ''
            print Fore.RED + "~> Hi, What can i do for you?" + Fore.RESET
        else:
            self.speak()
            print Fore.RED + "~> What can i do for you?" + Fore.RESET

        try:
            user_data = raw_input()
        except ValueError:
            user_data = input()
        except:
            user_data = input()
        finally:
            # Set first_reaction to False in order to stop say "Hi" to user.
            self.first_reaction = False

        user_data = str.lower(user_data)
        return user_data

    def speak(self):
        if self.enable_voice:
            self.speech.speak(self.first_reaction)

    def find_action(self, data):
        """
        This method gets the data and assigns it to an action
        """
        user_wish = "null"
        for key in self.actions:
            if key in data:
                user_wish = self.actions[key]
        if user_wish in self.actions.values():
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
        while True:
            data = self.user_input()
            wish = self.find_action(data)
            self.reactions(wish, data)
