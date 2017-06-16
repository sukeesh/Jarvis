import unittest
import CmdInterpreter
from utilities import GeneralUtilities
from mock import patch


class HelpTest(unittest.TestCase):

    def setUp(self):
        self.CI = CmdInterpreter.CmdInterpreter
        initial_text = "This is Jarvis"
        prompt = "How can I help?"
        self.CI_instance = self.CI(initial_text, prompt)

    def test_print_say_called_for_all_cmd_help(self):
        unhelped_actions = ['help', 'chat', 'error']
        helped_actions = [action for action in self.CI_instance.actions if action not in unhelped_actions]
        for action in helped_actions:
            with patch('CmdInterpreter.print_say') as mock_print_say:
                if isinstance(action, dict):
                    action = action.keys()[0]
                help_cmd_name = "help_{}".format(action)
                help_cmd = getattr(self.CI, help_cmd_name)
                help_cmd(self.CI_instance)
                mock_print_say.assert_called()
