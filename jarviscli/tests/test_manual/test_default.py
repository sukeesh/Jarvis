import unittest
from Jarvis import Jarvis
from mock import patch


class DefaultTest(unittest.TestCase):

    def setUp(self):
        self.jarvis = Jarvis()
        self.action = {"enable": ["sound"]}

    # check that default is called if the second word of a two word command is not found in
    # the words_remaining ("enable cat and dog" instead of "enable your sound please")
    def test_call_default_for_wrong_dict_cmd(self):
        with patch.object(self.jarvis, 'default') as default_mock:
            self.jarvis._generate_output_if_dict(
                self.action, "enable", ["cat", "and", "dog"])
            self.assertTrue(default_mock.called)

    def test_dont_call_default_for_correct_dict_cmd(self):
        with patch.object(self.jarvis, 'default') as default_mock:
            self.jarvis._generate_output_if_dict(
                self.action, "enable", ["your", "sound", "please"])
            self.assertFalse(default_mock.called)

    # check that default is called if the first word of a several word command is used alone
    def test_call_default_if_1_word_only_dict_cmd(self):
        with patch.object(self.jarvis, 'default') as default_mock:
            self.jarvis.precmd("enable")
            self.assertTrue(default_mock.called)

    # check that default is called if the first word of a several word command is used
    # with words before it, but no words after
    def test_call_default_for_words_before_1_word_dict_cmd(self):
        args = (self.action, "enable", [])

        # check that _generate_output_if_dict is called with the expected arguments
        with patch.object(self.jarvis, '_generate_output_if_dict') as generate_output_mock:
            self.jarvis.precmd("please, could you enable")
            self.assertTrue(generate_output_mock.called)
            generate_output_mock.assert_called_once_with(*args)

        # check that _generate_output_if_dict calls default given these arguments
        with patch.object(self.jarvis, 'default') as default_mock:
            self.jarvis._generate_output_if_dict(*args)
            self.assertTrue(default_mock.called)
