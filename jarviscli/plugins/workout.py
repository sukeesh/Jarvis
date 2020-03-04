from plugin import plugin
from colorama import Fore


def pushups(jarvis, s):
	try:
		maximum = int(s);
	except:
		jarvis.say("Please enter an integer only!", Fore.BLUE)
		quit(jarvis)
		return
	num = maximum*2//5
	rest = 30
	jarvis.say("Your program for today is 5 sets of " + str(num) + " times with rests of " + str(rest) + "sec", Fore.BLUE);
	s = jarvis.input("Type 's' to start and 'q' for quit\n", Fore.GREEN)
	if (s == "'q'" or s == "q"):
		quit(jarvis)
	elif (s == "'s'" or s == "s"):
		for i in range(1,6):
			jarvis.say("Set "+ str(i) + " Do " + str(num) + " times", Fore.BLUE)
			jarvis.input("Press enter after finishing", Fore.GREEN)
		jarvis.say("Well done, you did " + str(num*5) + " times pushups", Fore.BLUE)
		quit(jarvis)
	else:
		jarvis.say("Incorrect input, please write either 'push' or 'pull'", Fore.BLUE)
		quit(jarvis)

def pullups(jarvis, s):
	try:
		int(s);
	except:
		jarvis.say("Please enter an integer only!", Fore.BLUE)
		quit(jarvis)
		return
	jarvis.say("do " + s + " times pullups");


def quit(jarvis):
	jarvis.say("Stay fit - do workout!", Fore.BLUE)


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