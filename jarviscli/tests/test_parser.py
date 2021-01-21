import unittest
import language.default
from plugin import plugin


def do_nothing():
    pass


class ParserTest(unittest.TestCase):
    def test_default(self):
        self._test(language.default.DefaultLanguageParser())

    def _test(self, language_parser):
        plugins = [
            plugin("joke")(do_nothing)(),
            plugin("trash")(do_nothing)(),
            plugin("test")(do_nothing)(),
            plugin("weather")(do_nothing)(),
            plugin("check")(do_nothing)(),
            plugin("goodbye")(do_nothing)(),
            plugin("say")(do_nothing)(),
            plugin("near")(do_nothing)()
        ]

        language_parser.train(plugins)

        user_input = "Jarvis, I want to hear a joke about Chuck Norris, can you help me?"
        parsed_input = language_parser.identify_action(user_input)
        self.assertEqual("joke", parsed_input.get_name())

        user_input = "Mmm... I want to go for a walk. What's the weather like today?"
        parsed_input = language_parser.identify_action(user_input)
        self.assertEqual("weather", parsed_input.get_name())

        user_input = "Thanks for your hard work Jarvis, goodbye!"
        parsed_input = language_parser.identify_action(user_input)
        self.assertEqual("goodbye", parsed_input.get_name())

        user_input = "It would be cool if you could check my computers ram"
        parsed_input = language_parser.identify_action(user_input)
        self.assertEqual("check", parsed_input.get_name())

        user_input = "Can you say I'm a robot"
        parsed_input = language_parser.identify_action(user_input)
        self.assertEqual("say", parsed_input.get_name())

        user_input = "charities near Valencia"
        parsed_input = language_parser.identify_action(user_input)
        self.assertEqual("near", parsed_input.get_name())


if __name__ == '__main__':
    unittest.main()
