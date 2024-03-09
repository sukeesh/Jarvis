import re

from colorama import Fore


class DefaultLanguageParser:
    def __init__(self):
        self.plugins = {}
        self.regex_dot = re.compile('\\.(?!\\w)')

    def train(self, plugins):
        self.plugins = plugins

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
        return self._find_action(data)

    def _find_action(self, data):
        """Checks if input is a defined action.
        :return: returns the action"""
        output = "None"
        action_plugin = None

        words = data.split()

        actions = list(self.plugins.keys())

        # return longest matching word
        # For now, this code returns acceptable results
        actions.sort(key=lambda l: len(l), reverse=True)

        # check word by word if exists an action with the same name
        for action in actions:
            words_remaining = data.split()
            for word in words:
                if word == action:
                    words_remaining.remove(word)
                    output = " ".join(words_remaining)
                    action_plugin = self.plugins[action]

                    return action_plugin

        return None
