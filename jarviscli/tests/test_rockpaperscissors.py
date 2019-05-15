import unittest
from tests import PluginTest
from plugins.rockpaperscissors import rockpaperscissors
from Jarvis import Jarvis


class RockpaperscissorsTest(PluginTest):
    """
        This class is testing the rockpaperscissors plugin
    """

    def setUp(self):
        self.test = self.load_plugin(rockpaperscissors)

    def test_1_r_vs_p(self):
        umove = "r"
        jmove = "p"
        result = self.test.game(umove, jmove)
        self.assertEqual(result, "L")

    def test_2_r_vs_s(self):
        umove = "r"
        jmove = "s"
        result = self.test.game(umove, jmove)
        self.assertEqual(result, "W")

    def test_3_r_vs_r(self):
        umove = "r"
        jmove = "r"
        result = self.test.game(umove, jmove)
        self.assertEqual(result, "T")

    def test_4_p_vs_r(self):
        umove = "p"
        jmove = "r"
        result = self.test.game(umove, jmove)
        self.assertEqual(result, "W")

    def test_5_p_vs_s(self):
        umove = "p"
        jmove = "s"
        result = self.test.game(umove, jmove)
        self.assertEqual(result, "L")

    def test_6_p_vs_p(self):
        umove = "p"
        jmove = "p"
        result = self.test.game(umove, jmove)
        self.assertEqual(result, "T")

    def test_7_s_vs_p(self):
        umove = "s"
        jmove = "p"
        result = self.test.game(umove, jmove)
        self.assertEqual(result, "W")

    def test_8_s_vs_r(self):
        umove = "s"
        jmove = "r"
        result = self.test.game(umove, jmove)
        self.assertEqual(result, "L")

    def test_9_s_vs_s(self):
        umove = "s"
        jmove = "s"
        result = self.test.game(umove, jmove)
        self.assertEqual(result, "T")

    if __name__ == '__main__':
        unittest.main()
