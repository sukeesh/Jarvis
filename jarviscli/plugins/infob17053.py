from plugin import plugin 
import random

def some_prog():
	print("Some Silly Program")
	for i in range(random.randint(1, 10)):
		print("Do nothing random no of times: This is",i,"time")

@plugin("infob17053")
class infob17053:

	def __call__(self, jarvis, s):
		x = "Welcome to the info plugin of Purushottam Sinha roll num b17053. Please select one of the options below:\n [F]ull name // prints your full name\n [H]ometown // prints your hometownFavourite \n [M]ovie // prints your fav movieFavourite \n [S]portsperson // prints your fav sportspersonLaunch \n [P]ython program written by me // launch a (short)// python program\n"
		u_input = jarvis.input(x)

		if u_input == 'F':
			jarvis.say("Purushottam Sinha")
		elif u_input == 'H':
			jarvis.say("BiharSharif")
		elif u_input == 'M':
			jarvis.say("3 Idiot")
		elif u_input == 'S':
			jarvis.say("MS Dhoni")
		elif u_input == 'P':
			some_prog()
		else:
			jarvis.say("Invalid Input") 
