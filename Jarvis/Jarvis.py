from os import system
from time import ctime
from colorama import Fore
from packages.music import play
from packages.todo import todoHandler
from packages import newws, mapps, picshow, evaluator
import pyttsx

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
        * We would like to report that "weather" command is not
        running and it crashes the whole program. We DID NOT
        modified any lines of code from weather, it was
        probably with bug the whole time. We will work on this
        issue and we hope we will find a way to overcome it.
        * Furthermore, "near me" command is unable to find
        the actual location of our laptops.
"""


class Jarvis:
    # We use this variable at Breakpoint #1.
    # We use this in order to allow Jarvis say "Hi", only at the first interaction.
    first_reaction = True

    def __init__(self):
        """
        This constructor contains a dictionary with Jarvis Actions (what Jarvis can do).
        """
        self.actions = {"how are you?": "how_are_you",
                        "weather": "weather",
                        "open camera": "open_camera",
                        "what time is it": "clock",
                        "where am i": "pinpoint",
                        "near me": "near_me",
                        "movies": "movies",
                        "music": "music",
                        "increase volume": "increase_volume",
                        "decrease volume": "decrease_volume",
                        "hotspot start": "hotspot_start",
                        "hotspot stop": "hotspot_stop",
                        "search for a string in file": "string_pattern",
                        "check ram": "check_ram",
                        "todo": "todo",
                        "news": "news",
                        "show me pics of": "display_pics",
                        "evaluate": "evaluate",
                        "show me directions from": "get_directions",
                        "quit": "quit",
                        "exit": "quit",
                        "goodbye": "quit",
                        "help": "help",
                        "error": "error"
                        }
        self.create()

    def speak(self):
        """
        This method allows Jarvis to speak!
        In order to learn more about the module used to perform this action
        go to the following link: https://pyttsx.readthedocs.io/en/latest/engine.html
        :return: Nothing to return.
        """
        if self.first_reaction:
            self.engine.say('Hi what can i do for you?'.encode('utf-8'))
            self.engine.runAndWait()
        else:
            self.create()
            self.engine.say("What can i do for you".encode('utf-8'))
            self.engine.runAndWait()
        self.destroy()

    def destroy(self):
        """
        This method destroys a pyttsx object...
        :return: Nothing to return.
        """
        del self.engine

    def create(self):
        """
        This method creates a pyttsx object.
        :return: Nothing to return
        """
        self.engine = pyttsx.init()
        self.engine.setProperty('rate', 120)

    def reactions(self, key):
        """
        This function contains local functions which are implementing
        Jarvis' actions.
        :param key: the action which corresponds to a local function
                    eg. key = (How are you) (according to actions dictionary)
                    corresponds to how_are_you() function.
        :return: This method does not return any objects.
        """
        def how_are_you():
            print(Fore.BLUE + "I am fine, How about you" + Fore.RESET)

        def weather():
            mapps.weather()

        def clock():
            print(Fore.BLUE + ctime() + Fore.RESET)

        def open_camera():
            print "Opening Cheese ...... "
            system("cheese")

        def pinpoint():
            mapps.locateme()

        def near_me():
            mapps.searchNear(key)

        def movies():
            try:
                movie_name = raw_input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)
            except:
                movie_name = input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)
            system("ims " + movie_name)

        def music():
            play(key)

        def increase_volume():
            system("pactl -- set-sink-volume 0 +3%")

        def decrease_volume():
            system("pactl -- set-sink-volume 0 -10%")

        def hotspot_start():
            system("sudo ap-hotspot start")

        def hotspot_stop():
            system("sudo ap-hotspot stop")

        def string_pattern():
            try:
                file_name = raw_input(Fore.RED + "Enter file name?:\n" + Fore.RESET)
                stringg = raw_input(Fore.GREEN + "Enter string:\n" + Fore.RESET)
            except:
                file_name = input(Fore.RED + "Enter file name?:\n" + Fore.RESET)
                stringg = input(Fore.GREEN + "Enter string:\n" + Fore.RESET)
            system("grep '" + stringg + "' " + file_name)

        def check_ram():
            system("free -lm")

        def todo():
            todoHandler(key)

        def news():
            newws.show_news()

        def display_pics():
            picshow.showpics(key)

        def evaluate():
            tempt = key.split(" ", 1) or ""
            if len(tempt) > 1:
                evaluator.calc(tempt[1])
            else:
                print(Fore.RED + "Error : Not in correct format" + Fore.RESET)

        def get_directions():
            mapps.directions(key)

        def quit():
            print(Fore.RED + "Goodbye, see you later!" + Fore.RESET)
            exit()

        def help():
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
            print Fore.GREEN + '[*] quit: Close the session with Jarvis...' + Fore.RESET
            print Fore.GREEN + '[*] exit: Close the session with Jarvis...' + Fore.RESET
            print Fore.GREEN + '[*] Goodbye: Close the session with Jarvis...' + Fore.RESET

        def error():
            """
            In case of an error or typo during user's input we notify the
            user that something went wrong or the command he send is not
            supported by Jarvis.
            :return: Nothing to return.
            """
            print Fore.RED + "I could not identify your command..." + Fore.RESET
        locals()[key]()  # we are calling the proper function which satisfies the user's command.

    def user_input(self):
        """
        This method is responsible for getting the user's input.
        We are using first_reaction variable in order to prompt
        "Hi" only the first time we "meet" our user (in your first version
        whenever you asked for a command Jarvis where saying "Hi").
        :return: user_wish, a variable containing the Jarvis' action
                 that user wants to execute.
        """
        # BREAKPOINT #1
        if self.first_reaction:
            #self.speak()
            print Fore.RED + "Hi, What can i do for you?" + Fore.RESET
        else:
            #self.speak()
            print Fore.RED + "What can i do for you?" + Fore.RESET

        try:
            user_wish = raw_input()
        except ValueError:
            user_wish = input()
        except:
            user_wish = input()
        finally:
            # Set first_reaction to False in order to stop say "Hi" to user.
            self.first_reaction = False

        if user_wish in self.actions.keys():
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
            self.speak()
            wish = self.actions[self.user_input()]
            self.reactions(wish)

