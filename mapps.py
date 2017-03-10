import os, json, requests
from colorama import init
from colorama import Fore, Back, Style

def directions(data):
	data = data.split(" ")
	from_city = data[4]
	to_city = data[6]
	url = "https://www.google.co.in/maps/dir/"
	url = url + str(from_city) + "/" + str(to_city)
	os.system("google-chrome-stable -app=" +  url)

def locateme():
	send_url = 'http://freegeoip.net/json'
	r = requests.get(send_url)
	j = json.loads(r.text)
	hcity = j['city']
	print(Fore.BLUE + "You are at " + hcity + Fore.RESET)

def weatherr():
	send_url = 'http://freegeoip.net/json'
	r = requests.get(send_url)
	j = json.loads(r.text)
	hcity = j['city']
	send_url = "http://api.openweathermap.org/data/2.5/weather?q=" + str(hcity) + "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9";
	r = requests.get(send_url)
	j = json.loads(r.text)
	weath = j['main']['temp']
	print(Fore.BLUE + "It's " + str(weath) + " Fahrenheit" + Fore.RESET)


def nearme(data):
	data = data.split(" ")
	things = data[0]
	print(Fore.GREEN + "Hold on!, I'll show " + things + " near you" + Fore.RESET)
	send_url = 'http://freegeoip.net/json'
	r = requests.get(send_url)
	j = json.loads(r.text)
	os.system("google-chrome-stable -app=https://www.google.co.in/maps/search/" + str(things) + "/@" + str(j['latitude']) + "," + str(j['longitude']))

