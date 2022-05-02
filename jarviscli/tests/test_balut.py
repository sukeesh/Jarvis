import unittest
import functools
import plugins.balut as b
from tests import PluginTest


class ScoreCalculatorTest(unittest.TestCase):

    def test_calc_same_face_score(self) -> None:
        expected_score = 2 * 4
        actual_score = b.calc_same_face_score(hand=[4, 2, 3, 4, 1], face=4)
        self.assertEqual(expected_score, actual_score)

        expected_score = 0 * 4
        actual_score = b.calc_same_face_score(hand=[2, 2, 3, 6, 1], face=4)
        self.assertEqual(expected_score, actual_score)

        expected_score = 3 * 5
        actual_score = b.calc_same_face_score(hand=[5, 5, 3, 5, 1], face=5)
        self.assertEqual(expected_score, actual_score)

        expected_score = 0 * 5
        actual_score = b.calc_same_face_score(hand=[2, 4, 3, 6, 1], face=5)
        self.assertEqual(expected_score, actual_score)

        expected_score = 2 * 6
        actual_score = b.calc_same_face_score(hand=[6, 2, 6, 2, 4], face=6)
        self.assertEqual(expected_score, actual_score)

        expected_score = 0 * 6
        actual_score = b.calc_same_face_score(hand=[1, 2, 3, 4, 5], face=6)
        self.assertEqual(expected_score, actual_score)

    def test_calc_straight_score(self) -> None:
        expected_score = 1 + 2 + 3 + 4 + 5
        actual_score = b.calc_straight_score(hand=[1, 2, 3, 4, 5])
        self.assertEqual(expected_score, actual_score)

        expected_score = 2 + 3 + 4 + 5 + 6
        actual_score = b.calc_straight_score(hand=[2, 3, 4, 5, 6])
        self.assertEqual(expected_score, actual_score)

        expected_score = 0
        actual_score = b.calc_straight_score(hand=[2, 2, 2, 5, 5])
        self.assertEqual(expected_score, actual_score)

    def test_calc_full_house_score(self) -> None:
        expected_score = 2 + 2 + 2 + 5 + 5
        actual_score = b.calc_full_house_score(hand=[2, 2, 2, 5, 5])
        self.assertEqual(expected_score, actual_score)

        expected_score = 5 + 5 + 5 + 6 + 6
        actual_score = b.calc_full_house_score(hand=[5, 5, 5, 6, 6])
        self.assertEqual(expected_score, actual_score)

        expected_score = 0
        actual_score = b.calc_full_house_score(hand=[2, 2, 2, 2, 2])
        self.assertEqual(expected_score, actual_score)

    def test_calc_choice_score(self) -> None:
        expected_score = 5 + 5 + 6 + 6 + 3
        actual_score = b.calc_choice_score(hand=[5, 5, 6, 6, 3])
        self.assertEqual(expected_score, actual_score)

        expected_score = 4 + 4 + 2 + 3 + 6
        actual_score = b.calc_choice_score(hand=[4, 4, 2, 3, 6])
        self.assertEqual(expected_score, actual_score)

    def test_calc_balut_score(self) -> None:
        BALUT_BASE_SCORE = 20

        expected_score = BALUT_BASE_SCORE + 5 * 4 
        actual_score = b.calc_balut_score(hand=[4, 4, 4, 4, 4])
        self.assertEqual(expected_score, actual_score)

        expected_score = BALUT_BASE_SCORE + 5 * 2
        actual_score = b.calc_balut_score(hand=[2, 2, 2, 2, 2])
        self.assertEqual(expected_score, actual_score)

        expected_score = 0
        actual_score = b.calc_balut_score(hand=[2, 2, 3, 3, 3])
        self.assertEqual(expected_score, actual_score)


class PointsCalculatorTest(unittest.TestCase):

    def test_calc_same_face_points(self) -> None:
        SAME_FACE_POINTS = 2

        expected_points = SAME_FACE_POINTS
        actual_points = b.calc_same_face_points(fields=[12, 12, 12, 16], face=4)
        self.assertEqual(expected_points, actual_points)

        expected_points = 0
        actual_points = b.calc_same_face_points(fields=[8, 8, 12, 12], face=4)
        self.assertEqual(expected_points, actual_points)

        expected_points = SAME_FACE_POINTS
        actual_points = b.calc_same_face_points(fields=[15, 20, 15, 15], face=5)
        self.assertEqual(expected_points, actual_points)

        expected_points = 0
        actual_points = b.calc_same_face_points(fields=[10, 15, 10, 0], face=5)
        self.assertEqual(expected_points, actual_points)

        expected_points = SAME_FACE_POINTS
        actual_points = b.calc_same_face_points(fields=[18, 18, 24, 18], face=6)
        self.assertEqual(expected_points, actual_points)

        expected_points = 0
        actual_points = b.calc_same_face_points(fields=[12, 18, 6, 0], face=6)
        self.assertEqual(expected_points, actual_points)

    def test_calc_straight_points(self) -> None:
        STRAIGHT_POINTS = 4

        expected_points = STRAIGHT_POINTS
        actual_points = b.calc_straight_points(fields=[15, 15, 20, 15])
        self.assertEqual(expected_points, actual_points)

        expected_points = STRAIGHT_POINTS
        actual_points = b.calc_straight_points(fields=[20, 20, 15, 15])
        self.assertEqual(expected_points, actual_points)

        expected_points = 0
        actual_points = b.calc_straight_points(fields=[15, 15, 15, 0])
        self.assertEqual(expected_points, actual_points)

    def test_calc_full_house_points(self) -> None:
        FULL_HOUSE_POINTS = 3

        expected_points = FULL_HOUSE_POINTS
        actual_points = b.calc_full_house_points(fields=[16, 11, 19, 20])
        self.assertEqual(expected_points, actual_points)

        expected_points = FULL_HOUSE_POINTS
        actual_points = b.calc_full_house_points(fields=[22, 27, 16, 21])
        self.assertEqual(expected_points, actual_points)

        expected_points = 0
        actual_points = b.calc_full_house_points(fields=[22, 27, 16, 0])
        self.assertEqual(expected_points, actual_points)

    def test_calc_choice_points(self) -> None:
        CHOICE_POINTS = 2

        expected_points = CHOICE_POINTS
        actual_points = b.calc_choice_points(fields=[24, 25, 25, 26])
        self.assertEqual(expected_points, actual_points)

        expected_points = CHOICE_POINTS
        actual_points = b.calc_choice_points(fields=[25, 25, 25, 25])
        self.assertEqual(expected_points, actual_points)

        expected_points = 0
        actual_points = b.calc_choice_points(fields=[22, 23, 25, 26])
        self.assertEqual(expected_points, actual_points)


    def test_calc_balut_points(self) -> None:
        POINTS_PER_BALUT = 2

        expected_points = 1 * POINTS_PER_BALUT
        actual_points = b.calc_balut_points([0, 0, 30, 0])
        self.assertEqual(expected_points, actual_points)

        expected_points = 2 * POINTS_PER_BALUT
        actual_points = b.calc_balut_points([45, 0, 0, 30])
        self.assertEqual(expected_points, actual_points)

        expected_points = 0 * POINTS_PER_BALUT
        actual_points = b.calc_balut_points([0, 0, 0, 0])
        self.assertEqual(expected_points, actual_points)


class CategoryTest(unittest.TestCase):

    def setUp(self) -> None:
        self.category_choice = b.Category()
        self.category_choice.init("Choice",
            b.calc_choice_score,
            b.calc_choice_points)

        self.category_balut = b.Category()
        self.category_balut.init("Balut",
            b.calc_balut_score,
            b.calc_balut_points)

    def test_label(self) -> None:
        self.assertEqual(self.category_choice.label, "Choice")
        self.assertEqual(self.category_balut.label, "Balut")

    def test_calc_score(self) -> None:
        self.assertEqual(self.category_choice.calc_score, b.calc_choice_score)
        self.assertEqual(self.category_balut.calc_score, b.calc_balut_score)

    def test_calc_points(self) -> None:
        self.assertEqual(self.category_choice.calc_points, b.calc_choice_points)
        self.assertEqual(self.category_balut.calc_points, b.calc_balut_points)


class BalutPluginTest(PluginTest):

    def setUp(self):
        self.test = self.load_plugin(b.BalutPlugin)

    def test_create_categories(self) -> None:
        fours, fives, sixes, straight, full_house, choice, balut = \
            self.test.create_categories()

        self.assertEqual(fours.label, "Fours")
        self.assertEqual(fours.calc_score.func,
            functools.partial(b.calc_same_face_score, face=4).func)
        self.assertEqual(fours.calc_score.keywords,
            functools.partial(b.calc_same_face_score, face=4).keywords)
        self.assertEqual(fours.calc_points.func,
            functools.partial(b.calc_same_face_points, face=4).func)
        self.assertEqual(fours.calc_points.keywords,
            functools.partial(b.calc_same_face_points, face=4).keywords)

        self.assertEqual(fives.label, "Fives")
        self.assertEqual(fives.calc_score.func,
            functools.partial(b.calc_same_face_score, face=5).func)
        self.assertEqual(fives.calc_score.keywords,
            functools.partial(b.calc_same_face_score, face=5).keywords)
        self.assertEqual(fives.calc_points.func,
            functools.partial(b.calc_same_face_points, face=5).func)
        self.assertEqual(fives.calc_points.keywords,
            functools.partial(b.calc_same_face_points, face=5).keywords)

        self.assertEqual(sixes.label, "Sixes")
        self.assertEqual(sixes.calc_score.func,
            functools.partial(b.calc_same_face_score, face=6).func)
        self.assertEqual(sixes.calc_score.keywords,
            functools.partial(b.calc_same_face_score, face=6).keywords)
        self.assertEqual(sixes.calc_points.func,
            functools.partial(b.calc_same_face_points, face=6).func)
        self.assertEqual(sixes.calc_points.keywords,
            functools.partial(b.calc_same_face_points, face=6).keywords)

        self.assertEqual(straight.label, "Straight")
        self.assertEqual(straight.calc_score, b.calc_straight_score)
        self.assertEqual(straight.calc_points, b.calc_straight_points)

        self.assertEqual(full_house.label, "Full House")
        self.assertEqual(full_house.calc_score, b.calc_full_house_score)
        self.assertEqual(full_house.calc_points, b.calc_full_house_points)

        self.assertEqual(choice.label, "Choice")
        self.assertEqual(choice.calc_score, b.calc_choice_score)
        self.assertEqual(choice.calc_points, b.calc_choice_points)

        self.assertEqual(balut.label, "Balut")
        self.assertEqual(balut.calc_score, b.calc_balut_score)
        self.assertEqual(balut.calc_points, b.calc_balut_points)
