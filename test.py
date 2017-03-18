def main(key):
	def Troll1():
		print 'it worked'
	def Troll2():
		print 'yo'
	locals()['Troll' + key]()

main('2')

