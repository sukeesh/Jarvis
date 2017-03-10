import os
import urllib
from bs4 import BeautifulSoup
from urllib import urlopen
from colorama import init
from colorama import Fore, Back, Style

def show_news():

	url = "https://news.google.co.in/"
	url = str(url)
	wp = urllib.urlopen(url)
	soup = BeautifulSoup(wp.read(),"lxml")
	title_to_be_shown = soup.findAll("span")
	cnt = 1
	title_contents = []
	parent_urls = []

	for i in title_to_be_shown:
		if i.get('class')!=None and "titletext" in i.get('class'):
			title_contents.append(str(i.get_text()))
			parent_urls.append(str(i.parent['url']))
			cnt = cnt + 1
			if cnt == 5:
				break

	news_contents = []
	divs = soup.findAll("div")
	cnt = 1
	for i in divs:
		if i.get('class')!=None and "esc-lead-snippet-wrapper" in i.get('class'):
			news_contents.append(str(i.get_text()))
			cnt = cnt + 1
			if cnt == 5:
				break

	i = 0
	i = int(i)
	while i < len(title_contents):
		print (Fore.GREEN + str(i + 1) + " - " + title_contents[i] + Fore.RESET)
		i = i + 1

	print("Type index to expand news\n")
	idx = int(raw_input())
	idx = idx - 1
	print( ">> " + Fore.BLUE + news_contents[idx] + Fore.RESET + "\n")
	print(Fore.RED + "\n Do you want to read more? (yes/no) : " + Fore.RESET)
	take_yn = str(raw_input())
	take_yn = str.lower(take_yn)
	if take_yn == "yes":
		os.system("google-chrome-stable -app=" + parent_urls[idx])
	else:
		return
