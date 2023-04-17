import unittest
from tests import PluginTest
from plugins import fruit


class FruitTest(PluginTest):
    def setUp(self):
        self.fruit = self.load_plugin(fruit.fruit)

    def test_valid_fruit(self):
        test_input = "apple"
        expected_output = "Genus: Malus"

        self.fruit.run(test_input)
        self.assertEqual(self.history_say().last_text(), expected_output)

    def test_invalid_fruit(self):
        test_input = "invalid_fruit"
        expected_output = "Invalid fruit name. Please enter a valid fruit name."

        self.fruit.run(test_input)
        self.assertEqual(self.history_say().last_text(), expected_output)


if __name__ == '__main__':
    unittest.main()
