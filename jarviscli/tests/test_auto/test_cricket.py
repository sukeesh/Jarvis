import unittest
from packages import cricket
import sys
import io
# try:  # python2
#     from StringIO import StringIO
# except ImportError:  # python3
#     from io import StringIO


class CricketTest(unittest.TestCase):
	def setUp(self):
		sys.stdout = io.StringIO()

	def testScoreCard(self):
		'''
		contract: a score card should be returned
		'''

		# simulate input and call cricket module
		sys.stdin = io.StringIO('2\n1\nn')
		cricket.score(self)
		
		# read output from cricket module and assert it is not None
		sys.stdout.seek(0)
		output = sys.stdout.read()
		self.assertIsNotNone(output)


	def testRefreshScore(self):
		'''
		contract: the latest score should be returned
		'''

		# simulate input and call cricket module
		sys.stdin = io.StringIO('2\n3\nn')
		cricket.score(self)

		# read output from cricket module and assert it is not None
		sys.stdout.seek(0)
		output = sys.stdout.read()
		self.assertIsNotNone(output)

	def testComments(self):
		'''
		contract: the latest comments should be returned
		'''

		# simulate input and call cricket module
		sys.stdin = io.StringIO('2\n2\nn')
		cricket.score(self)

		# read output from cricket module and assert it is not None
		sys.stdout.seek(0)
		output = sys.stdout.read()
		self.assertIsNotNone(output)

	def testWrongChoice(self):
		'''
		contract: a wrong choice, and then correct to return a scorecard should work
		'''

		# simulate input and call cricket module
		sys.stdin = io.StringIO('32193\n2\n127843\n1\nn')
		cricket.score(self)
		
		# read output from cricket module and assert it is not None
		sys.stdout.seek(0)
		output = sys.stdout.read()
		self.assertIsNotNone(output)



	def tearDown(self):
		sys.stdin = sys.__stdin__
		sys.stdout = sys.__stdout__