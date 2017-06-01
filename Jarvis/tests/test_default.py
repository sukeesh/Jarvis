import unittest
from Jarvis import Jarvis
from mock import patch


class DefaultTest(unittest.TestCase):

    def setUp(self):
        self.jarvis = Jarvis()
        self.action = {"enable": ("sound",)}

    # check that default is called if the value of the word dictionary is not found in
    # the words_remaining ("enable cat and dog" instead of "enable your sound please")
    def test_call_default_for_wrong_dict_cmd(self):
        with patch.object(self.jarvis, 'default') as default_mock:
            self.jarvis._generate_output_if_dict(self.action, "enable", ["cat", "and", "dog"])
            self.assertTrue(default_mock.called)

    def test_dont_call_default_for_correct_dict_cmd(self):
        with patch.object(self.jarvis, 'default') as default_mock:
            self.jarvis._generate_output_if_dict(self.action, "enable", ["your", "sound", "please"])
            self.assertFalse(default_mock.called)
