from colorama import Fore
from os import system


class Jarvis:
    first_reaction = True
    def __init__(self):
        self.actions = {"how are you": "trash_talk",
                        "weather": "weather",
                        "open camera": "cheese",
                        }

    def user_input(self):
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
            self.first_reaction = False

        if user_wish in self.actions.keys():
            return user_wish
        return "error"

    def reactions(self, key):

        def trash_talk():
            print ("good")

        def weather():
            pass

        def cheese():
            pass

        def error():
            print Fore.RED + "I could not identify your command..." + Fore.RESET
        locals()[key]()


    def executor(self):
        wish = self.user_input()
        self.reactions(wish)

