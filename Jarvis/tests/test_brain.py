import unittest

from packages.aiml.brain import Brain


class BrainTest(unittest.TestCase):

    def test_memory(self):

        b = Brain()
        response = b.respond("TEST")
        self.assertEqual(str(response), 'TEST')


if __name__ == '__main__':
    unittest.main()
