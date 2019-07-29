import unittest
from tests import PluginTest
from plugins.timeconv import timeconv
from Jarvis import Jarvis


class TimeconvTest(PluginTest):
    """
        This class is testing the timeconv plugin
    """

    def setUp(self):
        self.test = self.load_plugin(timeconv)

    def test_0_ps2ns(self):
        amount = 30000.0
        from_unit = "ps"
        to_unit = "ns"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 30.0)

    def test_1_ns2mus(self):
        amount = 30000.0
        from_unit = "ns"
        to_unit = "mus"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 30.0)

    def test_2_mus2ms(self):
        amount = 30000.0
        from_unit = "mus"
        to_unit = "ms"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 30.0)

    def test_3_ms2s(self):
        amount = 30000.0
        from_unit = "ms"
        to_unit = "s"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 30.0)

    def test_4_s2min(self):
        amount = 120.0
        from_unit = "s"
        to_unit = "min"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 2.0)

    def test_5_min2h(self):
        amount = 120.0
        from_unit = "min"
        to_unit = "h"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 2.0)

    def test_6_h2d(self):
        amount = 72.0
        from_unit = "h"
        to_unit = "d"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 3.0)

    def test_7_d2wk(self):
        amount = 14.0
        from_unit = "d"
        to_unit = "wk"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 2.0)

    def test_8_wk2mon(self):
        amount = 4.2
        from_unit = "wk"
        to_unit = "mon"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 0.965934389583)

    def test_9_mon2yr(self):
        amount = 18.0
        from_unit = "mon"
        to_unit = "yr"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 1.5)

    def test_10_ns2ps(self):
        amount = 20.0
        from_unit = "ns"
        to_unit = "ps"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 20000.0)

    def test_11_mus2ns(self):
        amount = 30.0
        from_unit = "mus"
        to_unit = "ns"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 30000.0)

    def test_12_ms2mus(self):
        amount = 30.0
        from_unit = "ms"
        to_unit = "mus"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 30000.0)

    def test_13_s2ms(self):
        amount = 30.
        from_unit = "s"
        to_unit = "ms"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 30000.0)

    def test_14_min2s(self):
        amount = 3.0
        from_unit = "min"
        to_unit = "s"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 180.0)

    def test_15_h2min(self):
        amount = 2.0
        from_unit = "h"
        to_unit = "min"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 120.0)

    def test_16_d2h(self):
        amount = 3.0
        from_unit = "d"
        to_unit = "h"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 72.0)

    def test_17_wk2d(self):
        amount = 2.0
        from_unit = "wk"
        to_unit = "d"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 14.0)

    def test_18_mon2wk(self):
        amount = 2.0
        from_unit = "mon"
        to_unit = "wk"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 8.69624282)

    def test_19_yr2mon(self):
        amount = 2.0
        from_unit = "yr"
        to_unit = "mon"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 24.0)

    def test_20_s2d(self):
        amount = 86400.0
        from_unit = "s"
        to_unit = "d"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 1.0)

    def test_21_h2ms(self):
        amount = 2.0
        from_unit = "h"
        to_unit = "ms"
        convamount = self.test.time_convert(Jarvis, amount, from_unit, to_unit)
        self.assertEqual(convamount, 7200000.0)

    if __name__ == '__main__':
        unittest.main()
