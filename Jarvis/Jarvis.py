from os import system
from time import ctime
from colorama import Fore
from packages.music import play
from packages import newws, mapps, picshow, evaluator

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
                        "error": "error"
                        }

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
            mapps.weatherr()

        def clock():
            print(Fore.BLUE + ctime() + Fore.RESET)

        def open_camera():
            print "Opening Cheese ...... "
            system("cheese")

        def pinpoint():
            mapps.locateme()

        def near_me():
            mapps.nearme(key)

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
            todo.todoHandler(key)

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
            print Fore.RED + "Hi, What can i do for you?" + Fore.RESET
        else:
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
            wish = self.actions[self.user_input()]
            self.reactions(wish)

