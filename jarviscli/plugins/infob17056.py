from plugin import plugin
from colorama import Fore, Style

@plugin("infob17056")

def infob17056(jarvis,s):
    """
    This is a small plugin written by Sambhav Dusad.
    """
    jarvis.say(Fore.GREEN + "Welcome to the info plugin of Sambhav roll num B17056.")
    jarvis.say(Fore.CYAN + "Please select one of the options below:")
    jarvis.say("\t[F]ull name")
    jarvis.say("\t[H]ometown")
    jarvis.say("\tFavourite [M]ovie")
    jarvis.say("\tFavourite [S]portsperson")
    jarvis.say("\tLaunch [P]ython program written by me")
    jarvis.say(Fore.CYAN + '*Lets start? Type "q" to quit:')

    # Menu Implementation
    while(True):
    	#Take input
	    st = jarvis.input()
	    #Condition if user wants to quit
	    if st == 'q' or st == 'Q':
	    	jarvis.say(Fore.CYAN + 'Thank you for playing! New games are coming soon!')
	    	break
	    if st == 'F' or st == 'f':
	    	jarvis.say("My full name is Sambhav Dusad.")
	    elif st == 'H' or st == 'h':
	    	jarvis.say("My hometown is KonohaGakure No Satoru.")
	    elif st == 'M' or st == 'm':
	    	jarvis.say("My favourite movie is Naruto: The Movie.")
	    elif st == 'S' or st == 's':
	    	jarvis.say("My sportsperson is Goku.")
	    #Python program which concatenates two numbers
	    elif st == 'P' or st == 'p':
	    	jarvis.say(Fore.CYAN + "This is a python program which will add two numbers. Don't be surprised!!")
	    	jarvis.say("Enter first number")
	    	a = jarvis.input()
	    	jarvis.say("Enter second number")
	    	b = jarvis.input()
	    	c = a+b
	    	jarvis.say(c)