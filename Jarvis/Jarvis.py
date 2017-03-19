from colorama import Fore
from os import system
from packages import todo, newws, mapps, picshow, evaluator, audioHandler, music


class Jarvis:
    #first_reaction = True
    def __init__(self):
        self.actions = {"how are you": "how_are_you",
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
                        "goodbye": "quit"
                        }
                        
    def reactions(self, key):

        def how_are_you():
            print(Fore.BLUE + "I am fine, How about you" + Fore.RESET)

        def weather():
            mapps.weatherr()

        def clock():
            print(Fore.BLUE + ctime() + Fore.RESET)

        def open_camera():
            go("Opening Cheese ...... ")
            system("cheese")

        def pinpoint():
            mapps.locateme()

        def near_me():
            mapps.nearme(data)

        def movies():
            try:
                movie_name = raw_input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)
            except:
                movie_name = input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)
            system("ims " + movie_name)

        def music():
            music.play(data)

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
            todo.todoHandler(data)

        def news():
            newws.show_news()

        def display_pics():
            picshow.showpics(data)

        def evaluate():
            tempt = data.split(" ", 1) or ""
            if len(tempt) > 1:
                evaluator.calc(tempt[1])
            else:
                print(Fore.RED + "Error : Not in correct format" + Fore.RESET)

        def get_directions():
            mapps.directions(data)

        def quit():
            print(Fore.RED + "Goodbye, see you later!" + Fore.RESET)
            exit()

        def error():
            print Fore.RED + "I could not identify your command..." + Fore.RESET
        locals()[key]()

    def user_input(self):
        """
        if self.first_reaction:
            print Fore.RED + "Hi, What can i do for you?" + Fore.RESET
        else:
            print Fore.RED + "What can i do for you?" + Fore.RESET

        try:
        """
        print Fore.RED + "Hi, What can i do for you?" + Fore.RESET
        user_wish = raw_input()
        """
        except ValueError:
            user_wish = input()
        except:
            user_wish = input()
        finally:
            self.first_reaction = False

        if user_wish in self.actions.keys():
            return user_wish
        return "error"
        """
        return user_wish

    def executor(self):
        wish = self.user_input()
        self.reactions(wish)

