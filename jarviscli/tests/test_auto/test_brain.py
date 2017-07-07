import unittest

from packages.aiml.brain import Brain


class BrainTest(unittest.TestCase):

    def test_memory(self):

        b = Brain()

        # create all new brain file
        b.remove_brain()
        b.create_brain()
        response = b.respond("What are you")
        self.assertEqual(str(response), "I'm a bot, silly!")


if __name__ == '__main__':
    unittest.main()
