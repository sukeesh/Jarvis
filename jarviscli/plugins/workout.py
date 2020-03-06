from plugin import plugin
from colorama import Fore
import time

def pushComputeRest(maximum):
	if(maximum<25):
		rest = 30
	elif(maximum<50):
		rest = 45
	elif(maximum<75):
		rest = 60
	elif(maximum<100):
		rest = 75
	else:
		rest = 90
	return rest

def pushComputeNum(maximum):
	num = maximum*2//5
	num = int(num)
	return num

def pullComputeRest(maximum):
	if(maximum<10):
		rest = 30
	elif(maximum<15):
		rest = 45
	elif(maximum<20):
		rest = 60
	elif(maximum<25):
		rest = 75
	else:
		rest = 90
	return rest

def pullComputeNum(maximum):
	num = maximum*1.5//5
	num = int(num)
	return num

def pushups(jarvis, s):
	try:
		maximum = int(s);
	except:
		jarvis.say("Please enter an integer only!", Fore.BLUE)
		quit(jarvis)
		return
	num = pushComputeNum(maximum)
	rest = pushComputeRest(maximum)
	jarvis.say("Your program for today is 5 sets, each set is " + str(num) + " repetition with rests of " + str(rest) + " sec in between", Fore.BLUE);
	s = jarvis.input("Type 's' to start and 'q' for quit\n", Fore.GREEN)
	if (s == "'q'" or s == "q"):
		quit(jarvis)
	elif (s == "'s'" or s == "s"):
		for i in range(1,6):
			jarvis.say("Start Set "+ str(i) + " - Do " + str(num) + " pushups", Fore.RED)
			jarvis.input("Press enter after finishing", Fore.GREEN)
			jarvis.say("Rest: " + str(rest)+ " sec...", Fore.BLUE)
			jarvis.say("I will notice you when to start the next set\n", Fore.BLUE)
			time.sleep(2)
		jarvis.say("Well done, you performed " + str(num*5) + " pushups", Fore.BLUE)
		quit(jarvis)
	else:
		jarvis.say("Incorrect input, please write either 'push' or 'pull'", Fore.BLUE)
		quit(jarvis)

def pullups(jarvis, s):
	try:
		maximum = int(s);
	except:
		jarvis.say("Please enter an integer only!", Fore.BLUE)
		quit(jarvis)
		return
	num = pullComputeNum(maximum)
	rest = pullComputeRest(maximum)
	jarvis.say("Your program for today is 5 sets, each set is " + str(num) + " repetition with rests of " + str(rest) + " sec in between", Fore.BLUE);
	s = jarvis.input("Type 's' to start and 'q' for quit\n", Fore.GREEN)
	if (s == "'q'" or s == "q"):
		quit(jarvis)
	elif (s == "'s'" or s == "s"):
		for i in range(1,6):
			jarvis.say("Start Set "+ str(i) + " - Do " + str(num) + " pullups", Fore.RED)
			jarvis.input("Press enter after finishing", Fore.GREEN)
			jarvis.say("Rest: " + str(rest)+ " sec...", Fore.BLUE)
			jarvis.say("I will notice you when to start the next set\n", Fore.BLUE)
			time.sleep(2)
		jarvis.say("Well done, you performed " + str(num*5) + " pullups", Fore.BLUE)
		quit(jarvis)
	else:
		jarvis.say("Incorrect input, please write either 'push' or 'pull'")
		quit(jarvis)


def quit(jarvis):
	jarvis.say("Stay fit - do workout!", Fore.BLUE)


@plugin("workout")
def workout(jarvis, s):
    """Provides a workout programm according to user's abilities
    Formula to generate a relevant program is taken from:
    https://www.gbpersonaltraining.com/how-to-perform-100-push-ups/"""
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