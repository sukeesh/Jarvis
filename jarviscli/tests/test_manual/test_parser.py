import unittest
from Jarvis import Jarvis


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.jarvis = Jarvis()

    def test_chuck(self):
        user_input = "Jarvis, I want to hear a joke about Chuck Norris, can you help me?"
        parsed_input = self.jarvis.parse_input(user_input).split()
        self.assertEqual("chuck", parsed_input[0])

    def test_weather(self):
        user_input = "Mmm... I want to go for a walk. What's the weather like today?"
        parsed_input = self.jarvis.parse_input(user_input).split()
        self.assertEqual("weather", parsed_input[0])

    def test_goodbye(self):
        user_input = "Thanks for your hard work Jarvis, goodbye!"
        parsed_input = self.jarvis.parse_input(user_input).split()
        self.assertEqual("goodbye", parsed_input[0])

    def test_check_ram(self):
        user_input = "It would be cool if you could check my computers ram"
        parsed_input = self.jarvis.parse_input(user_input).split()
        self.assertEqual(["check"], parsed_input[0:1])

    def test_say(self):
        user_input = "Can you say I'm a robot"
        parsed_input = self.jarvis.parse_input(user_input).split()
        self.assertEqual(["say", "i'm", "a", "robot"], parsed_input[0:])

    def test_near(self):
        user_input = "charities near Valencia"
        parsed_input = self.jarvis.parse_input(user_input).split()
        self.assertEqual(
            ["near", "charities", "|", "valencia"], parsed_input[0:])


if __name__ == '__main__':
    unittest.main()
