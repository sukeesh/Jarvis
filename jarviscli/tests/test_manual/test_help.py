import unittest
import CmdInterpreter
from mock import patch
from utilities.GeneralUtilities import IS_MACOS

MACOS_BLACKLIST = {
    'movies',
    'music',
    'play',
}


class HelpTest(unittest.TestCase):

    def setUp(self):
        self.CI = CmdInterpreter.CmdInterpreter
        initial_text = "This is Jarvis"
        prompt = "How can I help?"
        self.CI_instance = self.CI(initial_text, prompt)

    def test_print_say_called_for_all_cmd_help(self):
        unhelped_actions = ['help', 'chat', 'error']
        helped_actions = [
            action for action in self.CI_instance.actions if action not in unhelped_actions]
        for action in helped_actions:
            with patch('CmdInterpreter.print_say') as mock_print_say:
                if isinstance(action, dict):
                    action = list(action.keys())[0]
                help_cmd_name = "help_{}".format(action)
                help_cmd = getattr(self.CI, help_cmd_name)
                help_cmd(self.CI_instance)
                if action in MACOS_BLACKLIST and IS_MACOS:
                    pass
                else:
                    mock_print_say.assert_called()
