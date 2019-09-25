from plugin import plugin
from colorama import Fore
import time

@plugin("infob17057")
def infob17057(jarvis, s):
	"""Command by B17057 ~ Saransh Sharma"""
	# Menu
	jarvis.say("Welcome to the info plugin of Saransh Sharma roll num B17057. Please select one of the options below:")
	jarvis.say(Fore.CYAN+"[F]ull name")
	jarvis.say(Fore.CYAN+"[H]ometown")
	jarvis.say(Fore.CYAN+"Favourite [M]ovie")
	jarvis.say(Fore.CYAN+"Favourite [S]portsperson")
	jarvis.say(Fore.CYAN+"Launch [P]ython program written by me")
	inp = jarvis.input()
	
	# Impementation of Menu
	if inp == 'F' or inp == 'f':
		jarvis.say("Hi! My name is Saransh Sharma.")
	elif inp == 'H' or inp == 'h':
		jarvis.say("I am from Delhi.")
	elif inp == 'M' or inp == 'm':
		jarvis.say("Well, that would be Megamind")
	elif inp == 'S' or inp == 's':
		jarvis.say("LeBron James")
	elif inp == 'P' or inp == 'p':
		jarvis.say("Sorry")
		i = int(1)	#Program
		while True:
			jarvis.say(
				Fore.GREEN
				+str(i))
			time.sleep(1)
			i = i + 1
	else:
		jarvis.say("Incorrect Selection")