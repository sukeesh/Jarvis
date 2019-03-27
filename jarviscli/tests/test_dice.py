import unittest
from plugins import dice
from tests import PluginTest
import random


class RollTest(PluginTest):
    def setUp(self):
        self.dice = self.load_plugin(dice.Roll)

    def test_help_examples(self):
        d = self.dice._dice_parse("Roll a dice")
        self.assertEqual(d["repeat"], 1)
        self.assertEqual(d["howmany"], 1)
        self.assertEqual(d["edges"], 6)
        self.assertFalse(self.dice._dice_is_error_in_config(d))

        d = self.dice._dice_parse("Roll four dices with 16 edges")
        self.assertEqual(d["repeat"], 1)
        self.assertEqual(d["howmany"], 4)
        self.assertEqual(d["edges"], 16)
        self.assertFalse(self.dice._dice_is_error_in_config(d))

        d = self.dice._dice_parse("Roll 5 dices five times")
        self.assertEqual(d["repeat"], 5)
        self.assertEqual(d["howmany"], 5)
        self.assertEqual(d["edges"], 6)
        self.assertFalse(self.dice._dice_is_error_in_config(d))

    def test_error_config(self):
        d = self.dice._dice_parse("1 Roll 0 dices with 20 edges 4 2 times 4 3")
        self.assertEqual(d["repeat"], 6)
        self.assertEqual(d["howmany"], 0)
        self.assertEqual(d["edges"], 20)
        self.assertTrue(self.dice._dice_is_error_in_config(d))

    def test_dice_roll(self):
        # test repeats
        for _ in range(5):
            # random config
            edges = random.randint(2, 10)
            repeat = random.randint(1, 10)
            howmany = random.randint(1, 10)

            config = {"repeat": repeat, "howmany": howmany, "edges": edges}
            result_check = [False] * edges

            # execute "roll" 500 times
            for _ in range(500):
                d = [x for x in self.dice._dice_roll(config)]

                # validate
                self.assertEqual(len(d), repeat)
                for row in d:
                    self.assertEqual(len(row), howmany)
                    for number in row:
                        number = int(number)
                        self.assertTrue(number > 0)
                        self.assertTrue(number <= edges)

            # make sure every number was thrown
                        result_check[number - 1] = True

            for b in result_check:
                self.assertTrue(b)


if __name__ == '__main__':
    unittest.main()
