import unittest
from colorama import Fore
from tests import PluginTest
from mock import patch
from plugins import cryptotracker


class TestCryptotracker(PluginTest):
    """
    A test class that contains test cases for the methods of
    the cryptotracker plugin.
    """

    def setUp(self):
        self.module = self.load_plugin(cryptotracker.main)

    def test_print_in_color_red(self):
        change = -1.54
        colored_text = Fore.RED + str(change) + Fore.RESET
        self.assertEqual(cryptotracker.print_in_color(change),
                         colored_text)

    def test_print_in_color_green(self):
        change = 1.54
        colored_text = Fore.GREEN + str(change) + Fore.RESET
        self.assertEqual(cryptotracker.print_in_color(change),
                         colored_text)

    @patch.object(cryptotracker, 'check_prices')
    def test_main_specific_pair(self, mock_check_prices):
        s = 'BTC/USD'
        base_expected = 'BTC'
        target_expected = 'USD'
        self.module.run(s)
        mock_check_prices.assert_called_with(base_expected, target_expected)

    @patch.object(cryptotracker, 'check_prices')
    def test_main_default_list(self, mock_check_prices):
        s = ''
        base_expected = ['BTC', 'ETH', 'LTC', 'XRP', 'ADA']
        target_expected = 'USD'
        self.module.run(s)
        expected_calls = [(i, target_expected) for i in base_expected]
        self.assertTrue(mock_check_prices.call_args_list, expected_calls)

    @patch('builtins.print')
    def test_main_exception_message(self, mock_print):
        s = 'wrong argument'
        self.module.run(s)
        mock_print.assert_called_with(
            "{WARNING}Wrong format!{COLOR_RESET} "
            "Try {ADVICE}cryptotracker base_currency/target_currency{COLOR_RESET} OR "
            "{ADVICE}cryptotracker{COLOR_RESET}".format(
                WARNING=Fore.RED, ADVICE=Fore.BLUE, COLOR_RESET=Fore.RESET))

    @patch('builtins.print')
    def test_check_prices_exception_message(self, mock_print):
        target = "wrong_currency"
        base = "wrong_currency"
        cryptotracker.check_prices(target, base)
        mock_print.assert_called_with(
            "{WARNING}Wrong pair {}/{}!{COLOR_RESET} "
            "\nFull list of symbols is here: "
            "https://coinmarketcap.com/all/views/all/"
            "\n".format(
                base,
                target,
                WARNING=Fore.RED,
                COLOR_RESET=Fore.RESET))


if __name__ == '__main__':
    unittest.main()
