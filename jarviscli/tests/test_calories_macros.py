import unittest
from tests import PluginTest
from typing import Callable
from plugins.calories_macros import CaloriesMacrosPlugin


class CaloriesMacrosPluginTest(PluginTest):

    def setUp(self):
        self.test = self.load_plugin(CaloriesMacrosPlugin)

    def test_validate_gender_valid(self):
        # Male (m/M)
        self.assertTrue(self.test.validate_gender("m"))
        self.assertTrue(self.test.validate_gender("M"))

        # Female (f/F)
        self.assertTrue(self.test.validate_gender("f"))
        self.assertTrue(self.test.validate_gender("F"))

    def test_validate_gender_invalid(self):
        # Anything other than Male (m/M) or Female (f/F)
        self.assertFalse(self.test.validate_gender("7"))
        self.assertFalse(self.test.validate_gender("s"))

    def test_validate_input_age_valid(self):
        bool_expression: Callable[[int], bool] = lambda age: age < 14

        # Anything greater than or equal to 14
        self.assertTrue(self.test.validate_input("14", bool_expression))
        self.assertTrue(self.test.validate_input("77", bool_expression))

    def test_validate_input_age_invalid(self):
        bool_expression: Callable[[int], bool] = lambda age: age < 14

        # Anything less than 14
        self.assertFalse(self.test.validate_input("13", bool_expression))
        self.assertFalse(self.test.validate_input("-1", bool_expression))

    def test_validate_input_height_valid(self):
        bool_expression: Callable[[int], bool] = lambda height: height <= 0

        # Anything greater than 0
        self.assertTrue(self.test.validate_input("1", bool_expression))
        self.assertTrue(self.test.validate_input("177", bool_expression))

    def test_validate_input_height_invalid(self):
        bool_expression: Callable[[int], bool] = lambda height: height <= 0

        # Anything less than or equal to 0
        self.assertFalse(self.test.validate_input("0", bool_expression))
        self.assertFalse(self.test.validate_input("-1", bool_expression))

    def test_validate_input_weight_valid(self):
        bool_expression: Callable[[int], bool] = lambda weight: weight <= 0

        # Anything greater than 0
        self.assertTrue(self.test.validate_input("1", bool_expression))
        self.assertTrue(self.test.validate_input("77", bool_expression))

    def test_validate_input_weight_invalid(self):
        bool_expression: Callable[[int], bool] = lambda weight: weight <= 0

        # Anything less than or equal to 0
        self.assertFalse(self.test.validate_input("0", bool_expression))
        self.assertFalse(self.test.validate_input("-1", bool_expression))

    def test_validate_input_workout_level_valid(self):
        bool_expression: Callable[[int], bool] = \
            lambda workout_level: not(1 <= workout_level <= 4)

        # Anything between 1 to 4
        self.assertTrue(self.test.validate_input("1", bool_expression))
        self.assertTrue(self.test.validate_input("2", bool_expression))
        self.assertTrue(self.test.validate_input("3", bool_expression))
        self.assertTrue(self.test.validate_input("4", bool_expression))

    def test_validate_workout_level_invalid(self):
        bool_expression: Callable[[int], bool] = \
            lambda workout_level: not(1 <= workout_level <= 4)

        # Anything other than the values 1 through 4
        self.assertFalse(self.test.validate_input("0", bool_expression))
        self.assertFalse(self.test.validate_input("5", bool_expression))

    def test_validate_input_goal_valid(self):
        bool_expression: Callable[[int], bool] = lambda goal: not(1 <= goal <= 3)

        # Anything between 1 to 3
        self.assertTrue(self.test.validate_input("1", bool_expression))
        self.assertTrue(self.test.validate_input("2", bool_expression))
        self.assertTrue(self.test.validate_input("3", bool_expression))

    def test_validate_goal_invalid(self):
        bool_expression: Callable[[int], bool] = lambda goal: not(1 <= goal <= 3)

        # Anything other than the values 1 through 3
        self.assertFalse(self.test.validate_input("0", bool_expression))
        self.assertFalse(self.test.validate_input("4", bool_expression))

    def test_validate_macro_ratios_valid(self):
        # Proteins at the lower bound and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.1, 0.6, 0.3))

        # Proteins at the upper bound and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.35, 0.45, 0.2))

        # Carbs at the lower bound and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.25, 0.45, 0.3))

        # Carbs at the upper bound and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.15, 0.65, 0.2))

        # Fats at the lower bound and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.2, 0.6, 0.2))

        # Fats at the upper bound and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.15, 0.5, 0.35))

        # All macros in range and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.15, 0.6, 0.25))
        self.assertTrue(self.test.validate_macro_ratios(0.25, 0.55, 0.20))

    def test_validate_macro_ratios_invalid(self):
        # Proteins slightly less than the lower bound and sum equal to 1
        self.assertFalse(self.test.validate_macro_ratios(0.09, 0.61, 0.3))

        '''
        Proteins slightly more than the upper bound cannot have sum equal to 1
        without violating the ratio of another macronutrient as well.
        '''

        # Carbs slightly less than the lower bound and sum equal to 1
        self.assertFalse(self.test.validate_macro_ratios(0.3, 0.44, 0.26))

        # Carbs slightly more than the upper bound and sum equal to 1
        self.assertFalse(self.test.validate_macro_ratios(0.12, 0.66, 0.22))

        # Fats slightly less than the lower bound and sum equal to 1
        self.assertFalse(self.test.validate_macro_ratios(0.21, 0.6, 0.19))

        # Fats slightly more than the upper bound and sum equal to 1
        self.assertFalse(self.test.validate_macro_ratios(0.14, 0.5, 0.36))

        # All macros in range and sum not equal to 1
        self.assertFalse(self.test.validate_macro_ratios(0.3, 0.6, 0.3))
        self.assertFalse(self.test.validate_macro_ratios(0.15, 0.5, 0.25))


if __name__ == '__main__':
    unittest.main()
