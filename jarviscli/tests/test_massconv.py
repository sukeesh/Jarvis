import unittest
from tests import PluginTest
from plugins.massconv import massconv
from Jarvis import Jarvis


class MassconvTest(PluginTest):
    """
        This class is testing the massconv plugin
    """

    def setUp(self):
        self.test = self.load_plugin(massconv)

    def test_0_mcg2mg(self):
        amount = 10
        from_unit = "mcg"
        to_unit = "mg"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 0.01)

    def test_1_mg2g(self):
        amount = 35
        from_unit = "mg"
        to_unit = "g"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 0.035)

    def test_2_g2kg(self):
        amount = 90
        from_unit = "g"
        to_unit = "kg"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 0.09)

    def test_3_kg2t(self):
        amount = 71200
        from_unit = "kg"
        to_unit = "t"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 71.2)

    def test_4_t2oz(self):
        amount = 6
        from_unit = "t"
        to_unit = "oz"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 211644)

    def test_5_oz2lb(self):
        amount = 20
        from_unit = "oz"
        to_unit = "lb"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 1.25)

    def test_6_lb2st(self):
        amount = 30
        from_unit = "lb"
        to_unit = "st"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 2.142858)

    def test_7_stone2cwt(self):
        amount = 40
        from_unit = "stone"
        to_unit = "cwt"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 5)

    def test_8_mg2mcg(self):
        amount = 16
        from_unit = "mg"
        to_unit = "mcg"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 16000)

    def test_9_g2mg(self):
        amount = 2
        from_unit = "g"
        to_unit = "mg"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 2000)

    def test_10_kg2g(self):
        amount = 3
        from_unit = "kg"
        to_unit = "g"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 3000)

    def test_11_t2kg(self):
        amount = 1.5
        from_unit = "t"
        to_unit = "kg"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 1500)

    def test_12_oz2t(self):
        amount = 12000
        from_unit = "oz"
        to_unit = "t"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 0.340193910529)

    def test_13_kg2oz(self):
        amount = 67
        from_unit = "kg"
        to_unit = "oz"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 2363.358)

    def test_14_gram2pound(self):
        amount = 14
        from_unit = "gram"
        to_unit = "pound"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 0.03086475)

    def test_15_lb2kg(self):
        amount = 10
        from_unit = "lb"
        to_unit = "kg"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 4.535918807053)

    def test_16_cwt2miligram(self):
        amount = 62
        from_unit = "cwt"
        to_unit = "miligram"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 3149740759.6215363)

    def test_17_st2kilogram(self):
        amount = 2
        from_unit = "st"
        to_unit = "kilogram"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 12.700567579522)

    def test_18_mcg2cwt(self):
        amount = 50
        from_unit = "mcg"
        to_unit = "cwt"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 9.84e-10)

    def test_19_cwt2mcg(self):
        amount = 32
        from_unit = "cwt"
        to_unit = "mcg"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 1625672622047.372)

    def test_20_ounce2gram(self):
        amount = 200
        from_unit = "ounce"
        to_unit = "gram"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 5669.898508816692)

    def test_21_microgram2pound(self):
        amount = 20000
        from_unit = "microgram"
        to_unit = "pound"
        convamount = self.test.mass_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 4.40925e-05)

    if __name__ == '__main__':
        unittest.main()
