from plugin import plugin
import os

def myprog():
	print("Custom Program")
	for i in range(4):
		print("Hey world!,",i)

@plugin('infob17106')
class Quote():
	'''
	infoB17106 gives information about B17106
	'''

	def __call__(self,jarvis,s):
		prompt=' Welcome to the info plugin of Tushar Tyagi, roll num B17106.Please select one of the options below: \n[F]ull Name\n[H]ometown\nFavorite [M]ovie\nFavorite [S]portsman\nLaunch [P]ython program written by me\n'
		user_input= jarvis.input(prompt)

		if user_input == 'F':
			jarvis.say('Tushar Tyagi')
		elif user_input == 'H':
			jarvis.say('Meerut')
		elif user_input == 'M':
			jarvis.say('Not any single')
		elif user_input == 'S':
			jarvis.say('Lee Chong Wie')
		elif user_input == 'P':
			myprog()
		else:
			jarvis.say('Invalid input')