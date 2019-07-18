import unittest
from tests import PluginTest
from plugins.bmi import Bmi


class BmiTest(PluginTest):
    """
        this class is testing the bmi plugin
    """

    def setUp(self):
        self.test = self.load_plugin(Bmi)

    def test_0_calc_bmi_m(self):
        height = 100
        weight = 100
        d = self.test.calc_bmi("m", height, weight)
        self.assertEqual(d, 100)

    def test_1_calc_bmi_m(self):
        height = 200
        weight = 100
        d = self.test.calc_bmi("m", height, weight)
        self.assertEqual(d, 25)

    def test_0_clac_bmi_i(self):
        height = 66
        weight = 154
        d = self.test.calc_bmi("i", height, weight)
        d = round(d, 0)
        self.assertEqual(d, 25)

    def test_1_clac_bmi_i(self):
        height = 75
        weight = 236
        d = self.test.calc_bmi("i", height, weight)
        d = round(d, 1)
        self.assertEqual(d, 29.5)


if __name__ == '__main__':
    unittest.main()
