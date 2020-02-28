from plugin import plugin
from colorama import Fore

@plugin("workout")
def workout(jarvis, s):
    """Provides a workout programm according to user's abilities"""
    s = jarvis.input("Choose an exercise. Write 'push' for pushups, 'pull' for pullups and 'q' for quit\n", Fore.GREEN)
    if (s == "'q'" or s == "q"):
    	quit(jarvis)
    elif (s == "'push'" or s == "push"):
    	s = jarvis.input("How many times do you do pushups? Please enter an integer!\n", Fore.GREEN)
    	pushups(jarvis, s)
    elif (s == "'pull'" or s == "pull"):
    	s = jarvis.input("How many times do you do pullups? Please enter an integer!\n", Fore.GREEN)
    	pullups(jarvis, s)
    else:
    	jarvis.say("Incorrect input, please write either 'push' or 'pull'", Fore.BLUE)
    	quit(jarvis)


def pushups(jarvis, s):
	try:
		int(s);
	except:
		jarvis.say("Please enter an integer only!", Fore.BLUE)
		quit(jarvis)
		return
	jarvis.say("do " + s + " times pushups");


def pullups(jarvis, s):
	try:
		int(s);
	except:
		jarvis.say("Please enter an integer only!", Fore.BLUE)
		quit(jarvis)
		return
	jarvis.say("do " + s + " times pullups");


def quit(jarvis):
	jarvis.say("Stay fit - do workout!", Fore.GREEN)
