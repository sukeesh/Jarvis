import unittest
from tests import PluginTest
from plugins.lengthconv import lengthconv
from Jarvis import Jarvis


class LengthconvTest(PluginTest):
    """
        This class is testing the lengthconv plugin
    """

    def setUp(self):
        self.test = self.load_plugin(lengthconv)

    def test_0_nm2mum(self):
        amount = 10
        from_unit = "nm"
        to_unit = "mum"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 0.01)

    def test_1_mum2mm(self):
        amount = 20
        from_unit = "mum"
        to_unit = "mm"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 0.02)

    def test_2_mm2cm(self):
        amount = 20
        from_unit = "mm"
        to_unit = "cm"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 2)

    def test_3_cm2dm(self):
        amount = 30
        from_unit = "cm"
        to_unit = "dm"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 3)

    def test_4_dm2m(self):
        amount = 20
        from_unit = "dm"
        to_unit = "m"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 2)

    def test_5_m2km(self):
        amount = 20
        from_unit = "m"
        to_unit = "km"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 0.02)

    def test_6_km2mi(self):
        amount = 30
        from_unit = "km"
        to_unit = "mi"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 18.64113576)

    def test_7_mi2yd(self):
        amount = 20
        from_unit = "mi"
        to_unit = "yd"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 35200)

    def test_8_yd2ft(self):
        amount = 20
        from_unit = "yd"
        to_unit = "ft"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 60)

    def test_9_ft2inch(self):
        amount = 30
        from_unit = "ft"
        to_unit = "in"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 360)

    def test_10_mum2nm(self):
        amount = 10
        from_unit = "mum"
        to_unit = "nm"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 10000)

    def test_11_mm2mum(self):
        amount = 20
        from_unit = "mm"
        to_unit = "mum"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 20000)

    def test_12_cm2mm(self):
        amount = 20
        from_unit = "cm"
        to_unit = "mm"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 200)

    def test_13_dm2cm(self):
        amount = 30
        from_unit = "dm"
        to_unit = "cm"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 300)

    def test_14_m2dm(self):
        amount = 20
        from_unit = "dm"
        to_unit = "m"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 2)

    def test_15_km2m(self):
        amount = 20
        from_unit = "km"
        to_unit = "m"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 20000)

    def test_16_mi2km(self):
        amount = 2
        from_unit = "mi"
        to_unit = "km"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 3.218688001229)

    def test_17_yd2mi(self):
        amount = 2
        from_unit = "yd"
        to_unit = "mi"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 0.001136363636)

    def test_18_ft2yd(self):
        amount = 1
        from_unit = "ft"
        to_unit = "yd"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 0.333333333333)

    def test_19_in2ft(self):
        amount = 2
        from_unit = "in"
        to_unit = "ft"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 0.166666666667)

    def test_20_cm2ft(self):
        amount = 200
        from_unit = "cm"
        to_unit = "ft"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 6.56167978752)

    def test_21_mi2m(self):
        amount = 20
        from_unit = "mi"
        to_unit = "m"
        convamount = self.test.length_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 32186.88001229384)

    if __name__ == '__main__':
        unittest.main()
