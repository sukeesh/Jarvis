import re

from colorama import Fore


class DefaultLanguageParser():
    def __init__(self, parser):
        self.plugins = {}
        self.regex_dot = re.compile('\\.(?!\\w)')
        self.parser = parser

    def train(self, plugins):
        self.plugins = plugins
        self.parser.pre_train(plugins)

    def identify_action(self, action):
        plugin = self._parse_input(action)
        return plugin

    def _parse_input(self, line):
        """This method gets the data and assigns it to an action"""
        data = line.lower()
        # say command is better if data has punctuation marks
        # Hack!
        if 'say' not in data:
            data = data.replace("?", "")
            data = data.replace("!", "")
            data = data.replace(",", "")
            data = data.replace(".", "")

            # Remove only dots not followed by alphanumeric character
            # to not mess up urls / numbers
            data = self.regex_dot.sub("", data)

        # if it doesn't have a fixed response, look if the data corresponds
        # to an action

        plugins = self.plugins
        last_plugin = None
        plugin_prefix = ''

        while True:
            sub_command, data = self._find_action(data, plugins, plugin_prefix)
            if sub_command is None:
                return last_plugin

            last_plugin = sub_command
            plugin_prefix += last_plugin.get_name() + ' '
            plugins = sub_command.get_plugins().values()

    def _find_action(self, data, actions, prefix):
        """Checks if input is a defined action.
        :return: returns the action"""
        output = "None"
        action_plugin = None


        return output, action_plugin