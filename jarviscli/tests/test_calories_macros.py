import unittest
from tests import PluginTest
from typing import Callable
from colorama import Fore
from plugins.calories_macros import CaloriesMacrosPlugin


class CaloriesMacrosPluginTest(PluginTest):

    def setUp(self):
        self.test = self.load_plugin(CaloriesMacrosPlugin)
        self.cal_calc_m = self.test.CalorieCalculator(
            gender="M",
            age=21,
            height=171,
            weight=69,
            activity_level=1,
            goal=1
        )
        self.cal_calc_f = self.test.CalorieCalculator(
            gender="F",
            age=24,
            height=166,
            weight=63,
            activity_level=3,
            goal=2
        )
        self.macro_calc_d = self.test.MacronutrientCalculator(
            daily_cal_intake=1750
        )
        self.macro_calc = self.test.MacronutrientCalculator(
            daily_cal_intake=2250,
            protein_ratio=0.3,
            carb_ratio=0.5,
            fat_ratio=0.2
        )

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
        bool_expression: Callable[[int], bool] = lambda age: age >= 14

        # Anything greater than or equal to 14
        self.assertTrue(self.test.validate_input("14", bool_expression))
        self.assertTrue(self.test.validate_input("77", bool_expression))

    def test_validate_input_age_invalid(self):
        bool_expression: Callable[[int], bool] = lambda age: age >= 14

        # Anything less than 14
        self.assertFalse(self.test.validate_input("13", bool_expression))
        self.assertFalse(self.test.validate_input("-1", bool_expression))

    def test_validate_input_height_valid(self):
        bool_expression: Callable[[int], bool] = lambda height: height > 0

        # Anything greater than 0
        self.assertTrue(self.test.validate_input("1", bool_expression))
        self.assertTrue(self.test.validate_input("177", bool_expression))

    def test_validate_input_height_invalid(self):
        bool_expression: Callable[[int], bool] = lambda height: height > 0

        # Anything less than or equal to 0
        self.assertFalse(self.test.validate_input("0", bool_expression))
        self.assertFalse(self.test.validate_input("-1", bool_expression))

    def test_validate_input_weight_valid(self):
        bool_expression: Callable[[int], bool] = lambda weight: weight > 0

        # Anything greater than 0
        self.assertTrue(self.test.validate_input("1", bool_expression))
        self.assertTrue(self.test.validate_input("77", bool_expression))

    def test_validate_input_weight_invalid(self):
        bool_expression: Callable[[int], bool] = lambda weight: weight > 0

        # Anything less than or equal to 0
        self.assertFalse(self.test.validate_input("0", bool_expression))
        self.assertFalse(self.test.validate_input("-1", bool_expression))

    def test_validate_input_workout_level_valid(self):
        bool_expression: Callable[[int], bool] = \
            lambda workout_level: 1 <= workout_level <= 4

        # Anything between 1 to 4
        self.assertTrue(self.test.validate_input("1", bool_expression))
        self.assertTrue(self.test.validate_input("2", bool_expression))
        self.assertTrue(self.test.validate_input("3", bool_expression))
        self.assertTrue(self.test.validate_input("4", bool_expression))

    def test_validate_workout_level_invalid(self):
        bool_expression: Callable[[int], bool] = \
            lambda workout_level: 1 <= workout_level <= 4

        # Anything other than the values 1 through 4
        self.assertFalse(self.test.validate_input("0", bool_expression))
        self.assertFalse(self.test.validate_input("5", bool_expression))

    def test_validate_input_goal_valid(self):
        bool_expression: Callable[[int], bool] = lambda goal: 1 <= goal <= 3

        # Anything between 1 to 3
        self.assertTrue(self.test.validate_input("1", bool_expression))
        self.assertTrue(self.test.validate_input("2", bool_expression))
        self.assertTrue(self.test.validate_input("3", bool_expression))

    def test_validate_goal_invalid(self):
        bool_expression: Callable[[int], bool] = lambda goal: 1 <= goal <= 3

        # Anything other than the values 1 through 3
        self.assertFalse(self.test.validate_input("0", bool_expression))
        self.assertFalse(self.test.validate_input("4", bool_expression))

    def test_validate_macro_ratios_valid(self):
        # Protein ratio at the lower bound and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.1, 0.6, 0.3))

        # Protein ratio at the upper bound and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.35, 0.45, 0.2))

        # Carb ratio at the lower bound and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.25, 0.45, 0.3))

        # Carb ratio at the upper bound and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.15, 0.65, 0.2))

        # Fat ratio at the lower bound and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.2, 0.6, 0.2))

        # Fat ratio at the upper bound and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.15, 0.5, 0.35))

        # All macro ratios in range and sum equal to 1
        self.assertTrue(self.test.validate_macro_ratios(0.15, 0.6, 0.25))
        self.assertTrue(self.test.validate_macro_ratios(0.25, 0.55, 0.20))

    def test_validate_macro_ratios_invalid(self):
        # Protein ratio slightly less than the lower bound and sum equal to 1
        self.assertFalse(self.test.validate_macro_ratios(0.09, 0.61, 0.3))

        '''
        Proteins slightly more than the upper bound cannot have sum equal to 1
        without violating the ratio of another macronutrient as well.
        '''

        # Carb ratio slightly less than the lower bound and sum equal to 1
        self.assertFalse(self.test.validate_macro_ratios(0.3, 0.44, 0.26))

        # Carb ratio slightly more than the upper bound and sum equal to 1
        self.assertFalse(self.test.validate_macro_ratios(0.12, 0.66, 0.22))

        # Fat ratio slightly less than the lower bound and sum equal to 1
        self.assertFalse(self.test.validate_macro_ratios(0.21, 0.6, 0.19))

        # Fat ratio slightly more than the upper bound and sum equal to 1
        self.assertFalse(self.test.validate_macro_ratios(0.14, 0.5, 0.36))

        # All macro ratios in range and sum not equal to 1
        self.assertFalse(self.test.validate_macro_ratios(0.3, 0.6, 0.3))
        self.assertFalse(self.test.validate_macro_ratios(0.15, 0.5, 0.25))

    def test_yellow(self):
        content = 'str_val'
        self.assertEqual(
            self.test.yellow(content), f'{Fore.YELLOW}{content}{Fore.RESET}')

    def test_red(self):
        content = 'str_val'
        self.assertEqual(
            self.test.red(content), f'{Fore.RED}{content}{Fore.RESET}')

    def test_read_gender(self):
        self.queue_input("7")  # invalid
        self.queue_input("s")  # invalid
        self.queue_input("m")  # valid

        input_msg = 'Gender (M/F): '
        error_msg = 'Oops! That was not a valid gender. Please try again (M/F)...'
        gender = self.test.read_gender(self.jarvis_api, input_msg, error_msg)

        self.assertEqual(self.history_say().view_text(0), self.test.red(error_msg))
        self.assertEqual(self.history_say().view_text(1), self.test.red(error_msg))
        self.assertEqual(gender, "M")

    def test_read_input_age(self):
        self.queue_input("-1")  # invalid
        self.queue_input("13")  # invalid
        self.queue_input("14")  # valid

        input_msg = 'Age: '
        bool_expression: Callable[[int], bool] = lambda age: age >= 14
        error_msg = ('We suggest you to consult a nutrition expert if you are '
            'under 14 years old.'
            '\nIf you made a mistake while entering your age, try again...')
        age = self.test.read_input(
            self.jarvis_api, input_msg, bool_expression, error_msg)

        self.assertEqual(self.history_say().view_text(0), self.test.red(error_msg))
        self.assertEqual(self.history_say().view_text(1), self.test.red(error_msg))
        self.assertEqual(age, 14)

    def test_read_input_height(self):
        self.queue_input("-1")  # invalid
        self.queue_input("0")   # invalid
        self.queue_input("1")   # valid

        input_msg = 'Height (cm): '
        bool_expression: Callable[[int], bool] = lambda height: height > 0
        error_msg = 'Oops! That was not a valid height. Try again...'
        height = self.test.read_input(
            self.jarvis_api, input_msg, bool_expression, error_msg)

        self.assertEqual(self.history_say().view_text(0), self.test.red(error_msg))
        self.assertEqual(self.history_say().view_text(1), self.test.red(error_msg))
        self.assertEqual(height, 1)

    def test_read_input_weight(self):
        self.queue_input("-1")  # invalid
        self.queue_input("0")   # invalid
        self.queue_input("1")   # valid

        input_msg = 'Weight (kg): '
        bool_expression: Callable[[int], bool] = lambda weight: weight > 0
        error_msg = 'Oops! That was not a valid weight. Try again...'
        weight = self.test.read_input(
            self.jarvis_api, input_msg, bool_expression, error_msg)

        self.assertEqual(self.history_say().view_text(0), self.test.red(error_msg))
        self.assertEqual(self.history_say().view_text(1), self.test.red(error_msg))
        self.assertEqual(weight, 1)

    def test_read_input_activity_level(self):
        self.queue_input("0")  # invalid
        self.queue_input("5")  # invalid
        self.queue_input("2")  # valid

        input_msg = 'Choose your activity level (1-4): '
        bool_expression: Callable[[int], bool] = \
            lambda activity_level: 1 <= activity_level <= 4
        error_msg = 'Oops! Invalid input. Try again (1-4)...'
        activity_level = self.test.read_input(
            self.jarvis_api, input_msg, bool_expression, error_msg)

        self.assertEqual(self.history_say().view_text(0), self.test.red(error_msg))
        self.assertEqual(self.history_say().view_text(1), self.test.red(error_msg))
        self.assertEqual(activity_level, 2)

    def test_read_input_goal(self):
        self.queue_input("0")  # invalid
        self.queue_input("4")  # invalid
        self.queue_input("3")  # valid

        input_msg = 'Choose your goal (1-3): '
        bool_expression: Callable[[int], bool] = lambda goal: 1 <= goal <= 3
        error_msg = 'Oops! Invalid input. Try again (1-3)...'
        goal = self.test.read_input(
            self.jarvis_api, input_msg, bool_expression, error_msg)

        self.assertEqual(self.history_say().view_text(0), self.test.red(error_msg))
        self.assertEqual(self.history_say().view_text(1), self.test.red(error_msg))
        self.assertEqual(goal, 3)

    def test_read_use_default_macro_ratios_accept(self):
        self.queue_input("y")
        use_default_macro_ratios = \
            self.test.read_use_default_macro_ratios(self.jarvis_api)
        self.assertTrue(use_default_macro_ratios)

    def test_read_use_default_macro_ratios_reject(self):
        self.queue_input("n")
        use_default_macro_ratios = \
            self.test.read_use_default_macro_ratios(self.jarvis_api)
        self.assertFalse(use_default_macro_ratios)

    def test_read_macro_ratios(self):
        # Invalid ratio
        self.queue_input("s")

        # Invalid combination
        self.queue_input("0.3")  # Protein ratio -> valid
        self.queue_input("0.4")  # Carb ratio -> invalid
        self.queue_input("0.3")  # Fat ratio -> valid

        # Valid combination
        self.queue_input("0.3")   # Protein ratio -> valid
        self.queue_input("0.45")  # Carb ratio -> valid
        self.queue_input("0.25")  # Fat ratio -> valid

        info_msg = ('\nThe recommended ratios for proteins are: '
            f'{self.test.yellow("0.1")} - {self.test.yellow("0.35")}\n'
            'The recommended ratios for carbs are: '
            f'{self.test.yellow("0.45")} - {self.test.yellow("0.65")}\n'
            'The recommended ratios for fats are: '
            f'{self.test.yellow("0.2")} - {self.test.yellow("0.35")}\n'
            'The macronutrient ratios you will provide must have a sum'
            'equal to one')
        error_msg = "Oops! That was not a valid ratio. Try again..."
        protein_ratio, carb_ratio, fat_ratio = \
            self.test.read_macro_ratios(self.jarvis_api, error_msg)

        # Invalid ratio
        self.assertEqual(self.history_say().view_text(0), info_msg)
        self.assertEqual(self.history_say().view_text(1), self.test.red(error_msg))

        # Invalid combination
        self.assertEqual(self.history_say().view_text(2), info_msg)

        # Valid combination
        self.assertEqual(self.history_say().view_text(3), info_msg)
        self.assertEqual(protein_ratio, 0.3)
        self.assertEqual(carb_ratio, 0.45)
        self.assertEqual(fat_ratio, 0.25)

    def test_display_welcome_message(self):
        self.test.display_welcome_message(self.jarvis_api)

        self.assertEqual(
            self.history_say().last_text(),
            self.test.yellow(
                '\nHello! In order to calculate your daily calorie intake '
                'i will need some information about you. Lets start...'))

    def test_display_activity_levels(self):
        self.test.display_activity_levels(self.jarvis_api)

        self.assertEqual(
            self.history_say().view_text(0),
            self.test.yellow("\nActivity levels:"))
        self.assertEqual(
            self.history_say().view_text(1),
            f'{self.test.yellow("[1]")} Little or no exercise')
        self.assertEqual(
            self.history_say().view_text(2),
            f'{self.test.yellow("[2]")} Light exercise 1-3 days a week')
        self.assertEqual(
            self.history_say().view_text(3),
            f'{self.test.yellow("[3]")} Moderate exercise 4-5 days a week')
        self.assertEqual(
            self.history_say().view_text(4),
            f'{self.test.yellow("[4]")} Hard exercise every day')

    def test_display_goals(self):
        self.test.display_goals(self.jarvis_api)

        self.assertEqual(
            self.history_say().view_text(0),
            self.test.yellow("\nGoals:"))
        self.assertEqual(
            self.history_say().view_text(1),
            f'{self.test.yellow("[1]")} Lose weight')
        self.assertEqual(
            self.history_say().view_text(2),
            f'{self.test.yellow("[2]")} Maintain weight')
        self.assertEqual(
            self.history_say().view_text(3),
            f'{self.test.yellow("[3]")} Gain weight')

    def test__calc_rmr(self):
        self.assertEqual(self.cal_calc_m._calc_rmr(), 1658.75)
        self.assertEqual(self.cal_calc_f._calc_rmr(), 1386.5)

    def test__calc_tdee(self):
        self.assertEqual(self.cal_calc_m._calc_tdee(1658.75), 1990)
        self.assertEqual(self.cal_calc_f._calc_tdee(1386.5), 2149)

    def test__calc_daily_calorie_intake(self):
        self.assertEqual(self.cal_calc_m._calc_daily_calorie_intake(1990), 1490)
        self.assertEqual(self.cal_calc_f._calc_daily_calorie_intake(2149), 2149)

    def test_calc_daily_calorie_intake(self):
        self.assertEqual(self.cal_calc_m.calc_daily_calorie_intake(), 1490)
        self.assertEqual(self.cal_calc_f.calc_daily_calorie_intake(), 2149)

    def test_display_calorie_results(self):
        with self.assertRaises(SystemExit):
            self.cal_calc_m.display_calorie_results(self.jarvis_api, 1490)
            self.assertEqual(
                self.history_say().last_text(),
                (f'{Fore.CYAN}\nThe calculated daily calorie intake was '
                'below the suggested of 1500 cal for males. We suggest you to '
                'consult a nutrition expert to help you achieve your goal!'))

        cal_intake = 2149
        self.cal_calc_f.display_calorie_results(self.jarvis_api, cal_intake)
        self.assertEqual(
            self.history_say().last_text(),
            ('\nThe recommended daily calorie intake to maintain '
            f'your current weight is: {Fore.YELLOW}{cal_intake}'))

    def test_calc_macros(self):
        protein_g, carb_g, fat_g = self.macro_calc_d.calc_macros()
        self.assertEqual(protein_g, 88)
        self.assertEqual(carb_g, 219)
        self.assertEqual(fat_g, 58)

        protein_g, carb_g, fat_g = self.macro_calc.calc_macros()
        self.assertEqual(protein_g, 169)
        self.assertEqual(carb_g, 281)
        self.assertEqual(fat_g, 50)

    def test_display_macros_results(self):
        protein_g, carb_g, fat_g = 88, 219, 58
        self.macro_calc_d.display_macros_results(
            self.jarvis_api, protein_g, carb_g, fat_g)

        self.assertEqual(
            self.history_say().view_text(0),
            ('Expressed in terms of macronutrients, that means that in '
            'a day you should eat:'))
        self.assertEqual(
            self.history_say().view_text(1),
            f'Proteins: {Fore.RED}{protein_g}g')
        self.assertEqual(
            self.history_say().view_text(2),
            f'Carbs: {Fore.GREEN}{carb_g}g')
        self.assertEqual(
            self.history_say().view_text(3),
            f'Fats: {Fore.YELLOW}{fat_g}g')


if __name__ == '__main__':
    unittest.main()
