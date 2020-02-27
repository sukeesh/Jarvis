from plugin import plugin
from colorama import Fore

@plugin("workout")
def helloworld(jarvis, s):
    """Provides a workout programm according to user's abilities"""
    s = jarvis.input("Choose an exercise. Press 'push' for pushups and 'pull' for pullups\n", Fore.GREEN)
    if (s == "'push'" or s == "push"):
    	s = jarvis.input("How many times do you do pushups?\n", Fore.GREEN)
    	jarvis.say("Do " + s + " times pushups")
    if (s == "'pull'" or s == "pull"):
    	s = jarvis.input("How many times do you do pullups?\n", Fore.GREEN)
    	jarvis.say("Do " + s + " times pullups")
