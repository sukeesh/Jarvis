import unittest
from tests import PluginTest
from plugins.calories import calories
from unittest.mock import patch


class CaloriesTest(PluginTest, unittest.TestCase):
    """
    This class is testing the calories plugin
    """

    def setUp(self):
        self.test = self.load_plugin(calories)

    def test_calories(self):
        gender = "m"
        age = 20
        height = 165
        weight = 54
        exercise_level = 3
        result = self.test.calories(gender, age, height, weight, exercise_level)
        self.assertEqual(result[0], 2096.4)
        self.assertEqual(result[1], 1596.4)
        self.assertEqual(result[2], 2596.4)

    def test_validate_gender_case1(self):
        correct_input = "m"
        self.assertTrue(self.test.validate_gender(correct_input))

    def test_validate_gender_case2(self):
        correct_input = "f"
        self.assertTrue(self.test.validate_gender(correct_input))

    def test_validate_gender_case2(self):
        wrong_input = "l"
        self.assertFalse(self.test.validate_gender(wrong_input))

    def test_validate_age_correct_input(self):
        correct_input = 21
        self.assertTrue(self.test.validate_age(correct_input))

    def test_validate_age_wrong_input(self):
        wrong_input1 = "age"
        wrong_input2 = -21
        self.assertFalse(self.test.validate_age(wrong_input1))
        self.assertFalse(self.test.validate_age(wrong_input2))

    def test_validate_height_correct_input(self):
        correct_input = 170
        self.assertTrue(self.test.validate_height(correct_input))

    def test_validate_height_wrong_input(self):
        wrong_input1 = "height"
        wrong_input2 = -170
        self.assertFalse(self.test.validate_height(wrong_input1))
        self.assertFalse(self.test.validate_height(wrong_input2))

    def test_validate_weight_correct_input(self):
        correct_input = 60
        self.assertTrue(self.test.validate_weight(correct_input))

    def test_validate_height_wrong_input(self):
        wrong_input1 = "weight"
        wrong_input2 = -170
        self.assertFalse(self.test.validate_weight(wrong_input1))
        self.assertFalse(self.test.validate_weight(wrong_input2))

    def test_validate_workout_level_correct_input(self):
        correct_input = 1
        self.assertTrue(self.test.validate_workout_level(correct_input))

    def test_validate_workout_level_wrong_input(self):
        wrong_input1 = "workout_level"
        wrong_input2 = -1
        self.assertFalse(self.test.validate_workout_level(wrong_input1))
        self.assertFalse(self.test.validate_workout_level(wrong_input2))

    def test_exercise_level(self):
        expected = 1.6
        result = self.test.exercise_level(3)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
