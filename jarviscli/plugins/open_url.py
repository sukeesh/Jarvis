from plugin import plugin
import urllib.request
from colorama import Fore
import webbrowser

@plugin('open link')
def openUrl(jarvis,s):
	""" Jarvis will open a browser link for you."""
	jarvis.say("Please enter a url: ", Fore.WHITE)
	url = input()
	jarvis.say("Opening the url....",Fore.GREEN)
	url1 = "https://"+url
	try:
		webbrowser.open(url1)
	except:
		url2 = "http://"+url
		webbrowser.open(url2) 
