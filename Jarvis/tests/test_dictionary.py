import unittest
from ..packages.dictonary import Thesaurus


class ThesaurusTest(unittest.TestCase):
    def test_dictinary(self):
        th = Thesaurus('Peace')
        self.assertIsNotNone(th.find())
