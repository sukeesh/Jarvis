import os
import urllib
from bs4 import BeautifulSoup
from urllib import urlopen
from colorama import init
from colorama import Fore, Back, Style

def showpics(strr):
	strr = strr.split(" ")
	query = strr[4]
	url = "'https://www.google.co.in/search?tbm=isch&q=" + str(query) + "'"
	os.system("google-chrome-stable -app=" + url)
