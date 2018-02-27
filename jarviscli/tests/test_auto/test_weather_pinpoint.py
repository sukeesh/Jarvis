from packages.memory.memory import Memory
from packages import weather_pinpoint
from Jarvis import Jarvis
import unittest
import sys
import os

class WeatherPinpointTest(unittest.TestCase) :
	def setUp(self) :
		self.jarvis = Jarvis()
		self.saved_stdin = sys.stdin
		self.saved_stdout = sys.stdout
		sys.stdout = open(os.devnull, 'w')
		self.mem = Memory()

	def test_no_location(self) :
		'''
		contract: a location shall be found with mapps
		'''
		infile = open('infile', 'w')
		infile.write('y\n')
		infile.close()
		sys.stdin = open('infile', 'r')
		self.mem.update_data('city', None)

		weather_pinpoint.main(self.mem, self.jarvis, '')
		self.assertIsNotNone(self.mem.get_data('city'))

	def test_no_location_umbrella(self) :
		'''
		contract: a location should be found with umbrella
		'''
		infile = open('infile', 'w')
		infile.write('y\n')
		infile.close()
		sys.stdin = open('infile', 'r')
		self.mem.update_data('city', None)

		weather_pinpoint.main(self.mem, self.jarvis, 'umbrella')
		self.assertIsNotNone(self.mem.get_data('city'))

	def test_not_change_location(self) :
		'''
		contract: our location does not change without our say-so
		'''
		infile = open('infile', 'w')
		infile.write('n\n')
		infile.close()
		sys.stdin = open('infile', 'r')
		self.mem.update_data('city', None)

		self.mem.update_data('city', 'NonExistentCity')
		weather_pinpoint.main(self.mem, self.jarvis, '')
		self.assertEqual(str(self.mem.get_data('city')), 'NonExistentCity')

	def test_change_location(self) :
		'''
		contract: our location changes when we say so
		'''
		infile = open('infile', 'w')
		infile.write('y\ny\n')
		infile.close()
		sys.stdin = open('infile', 'r')
		self.mem.update_data('city', None)

		self.mem.update_data('city', 'NonExistentCity')
		weather_pinpoint.main(self.mem, self.jarvis, '')
		self.assertNotEqual(str(self.mem.get_data('city')), 'NonExistentCity')

	def tearDown(self) :
		self.mem.del_data('city')
		sys.stdin.close()
		sys.stdout.close()
		os.remove('infile')
		sys.stdin = self.saved_stdin
		sys.stdout = self.saved_stdout
