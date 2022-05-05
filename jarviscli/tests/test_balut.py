import unittest
import functools
import plugins.balut as b
from copy import deepcopy
from tests import PluginTest
from unittest.mock import patch, call, Mock


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


class ScoresheetTest(PluginTest):
    MIN_CATEGORY = 1
    MAX_CATEGORY = 7

    def setUp(self) -> None:
        balut_plugin = self.load_plugin(b.BalutPlugin)
        self.categories = balut_plugin.create_categories()

        self.scoresheet = b.Scoresheet()
        self.scoresheet.init(
            self.categories,
            [
                [8, 8, 0, -1],
                [15, 15, -1, -1],
                [24, 6, 6, 0],
                [15, 0, 0, 0],
                [16, 12, 21, 7],
                [24, -1, -1, -1],
                [0, -1, -1, -1]
            ]
        )

    def test__validate_category_valid(self) -> None:
        self.assertTrue(self.scoresheet._validate_category(self.MIN_CATEGORY))
        self.assertTrue(self.scoresheet._validate_category(self.MAX_CATEGORY))

    def test__validate_category_invalid(self) -> None:
        with self.assertRaises(b.InvalidCategoryValueError) as e:
            self.scoresheet._validate_category(self.MIN_CATEGORY - 1)

        self.assertEqual(
            str(e.exception),
            'Oops! Category should be an integer between 1 and 7. Try again...\n')


        with self.assertRaises(b.InvalidCategoryValueError) as e:
            self.scoresheet._validate_category(self.MAX_CATEGORY + 1)

        self.assertEqual(
            str(e.exception),
            'Oops! Category should be an integer between 1 and 7. Try again...\n')


        with self.assertRaises(b.InvalidCategoryValueError) as e:
            self.scoresheet._validate_category(3)  # Category is full

        self.assertEqual(
            str(e.exception),
            'Oops! The category you selected is already full. Try again...\n')

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['txt','-1', '1'])
    def test_select_category_to_settle_score(self, mock_inputs, mock_print) -> None:
        category = self.scoresheet.select_category_to_settle_score()

        self.assertEqual(category, 1)

        calls = [
            call('Oops! Category should be an integer. Try again...\n'),
            call('Oops! Category should be an integer between 1 and 7. Try again...\n')
        ]
        mock_print.assert_has_calls(calls)

        input_calls = [
            call('Select the category to settle the score (1-7): '),
            call('Select the category to settle the score (1-7): '),
            call('Select the category to settle the score (1-7): ')
        ]
        mock_inputs.assert_has_calls(input_calls)

    def test__find_first_empty_field(self) -> None:
        self.assertEqual(self.scoresheet._find_first_empty_field(category=1), 3)
        self.assertEqual(self.scoresheet._find_first_empty_field(category=7), 1)

    def test__settle_score_to_field(self) -> None:
        scoresheet_cp = deepcopy(self.scoresheet)
        category, field, hand = 1, 3, [4, 4, 4, 3, 2]
        scoresheet_cp._settle_score_to_field(category, field, hand)

        self.assertNotEqual(
            scoresheet_cp._scoresheet_matrix[category - 1][field],
            self.scoresheet._scoresheet_matrix[category - 1][field])

        self.assertEqual(
            scoresheet_cp._scoresheet_matrix[category - 1][field],
            scoresheet_cp._categories[category - 1].calc_score(hand))

    def test_settle_score(self) -> None:
        scoresheet_cp = deepcopy(self.scoresheet)
        scoresheet_cp._find_first_empty_field = Mock()
        scoresheet_cp._settle_score_to_field = Mock()

        scoresheet_cp.settle_score(category=1, hand=[4, 4, 4, 3, 2])

        scoresheet_cp._find_first_empty_field.assert_called_once()
        scoresheet_cp._settle_score_to_field.assert_called_once()

    @patch('builtins.print')
    def test_display(self, mock_print) -> None:
        self.scoresheet.display()

        calls = [
            call('\n===================== Scoresheet ====================='),
            call('   Category     Field 1   Field 2   Field 3   Field 4  '),
            call('1  Fours           8         8         0         -     '),
            call('2  Fives           15        15        -         -     '),
            call('3  Sixes           24        6         6         0     '),
            call('4  Straight        15        0         0         0     '),
            call('5  Full House      16        12        21        7     '),
            call('6  Choice          24        -         -         -     '),
            call('7  Balut           0         -         -         -     '),
            call('======================================================\n')
        ]
        mock_print.assert_has_calls(calls)

    @patch('builtins.print')
    def test_display_with_score(self, mock_print) -> None:
        self.scoresheet.display_with_score([2, 3, 4, 5, 6])

        calls = [
            call('\n=========================== Scoresheet ==========================='),
            call('   Category     Field 1   Field 2   Field 3   Field 4  Score Gain'),
            call('1  Fours           8         8         0         -         +4    '),
            call('2  Fives           15        15        -         -         +5    '),
            call('3  Sixes           24        6         6         0        Full   '),
            call('4  Straight        15        0         0         0        Full   '),
            call('5  Full House      16        12        21        7        Full   '),
            call('6  Choice          24        -         -         -        +20    '),
            call('7  Balut           0         -         -         -         +0    '),
            call('==================================================================\n')
        ]
        mock_print.assert_has_calls(calls)

    def test__calc_total_score_points(self) -> None:
        self.assertEqual(self.scoresheet._calc_total_score_points(0), -2)
        self.assertEqual(self.scoresheet._calc_total_score_points(150), -2)
        self.assertEqual(self.scoresheet._calc_total_score_points(299), -2)

        self.assertEqual(self.scoresheet._calc_total_score_points(300), -1)
        self.assertEqual(self.scoresheet._calc_total_score_points(325), -1)
        self.assertEqual(self.scoresheet._calc_total_score_points(349), -1)

        self.assertEqual(self.scoresheet._calc_total_score_points(350), 0)
        self.assertEqual(self.scoresheet._calc_total_score_points(375), 0)
        self.assertEqual(self.scoresheet._calc_total_score_points(399), 0)

        self.assertEqual(self.scoresheet._calc_total_score_points(400), 1)
        self.assertEqual(self.scoresheet._calc_total_score_points(425), 1)
        self.assertEqual(self.scoresheet._calc_total_score_points(449), 1)

        self.assertEqual(self.scoresheet._calc_total_score_points(450), 2)
        self.assertEqual(self.scoresheet._calc_total_score_points(475), 2)
        self.assertEqual(self.scoresheet._calc_total_score_points(499), 2)

        self.assertEqual(self.scoresheet._calc_total_score_points(500), 3)
        self.assertEqual(self.scoresheet._calc_total_score_points(525), 3)
        self.assertEqual(self.scoresheet._calc_total_score_points(549), 3)

        self.assertEqual(self.scoresheet._calc_total_score_points(550), 4)
        self.assertEqual(self.scoresheet._calc_total_score_points(575), 4)
        self.assertEqual(self.scoresheet._calc_total_score_points(599), 4)

        self.assertEqual(self.scoresheet._calc_total_score_points(600), 5)
        self.assertEqual(self.scoresheet._calc_total_score_points(625), 5)
        self.assertEqual(self.scoresheet._calc_total_score_points(649), 5)

        self.assertEqual(self.scoresheet._calc_total_score_points(650), 6)
        self.assertEqual(self.scoresheet._calc_total_score_points(675), 6)
        self.assertEqual(self.scoresheet._calc_total_score_points(812), 6)

    def test_calc_points(self) -> None:
        complete_scoresheet_1 = b.Scoresheet()
        complete_scoresheet_1.init(
            self.categories,
            [
                [12, 12, 16, 12],  # 2 points
                [15, 15, 15, 10],  # 0 points
                [18, 24, 12, 18],  # 0 points
                [15, 0, 0, 0],     # 0 points
                [16, 12, 21, 7],   # 3 points
                [24, 26, 25, 25],  # 2 points
                [0, 0, 30, 0]      # 2 points
            ]                      # 0 points from total score (380)
        )
        self.assertEqual(complete_scoresheet_1.calc_points(), 9)

        complete_scoresheet_2 = b.Scoresheet()
        complete_scoresheet_2.init(
            self.categories,
            [
                [12, 12, 8, 0],    # 0 points
                [15, 15, 15, 20],  # 2 points
                [18, 24, 24, 18],  # 2 points
                [15, 20, 20, 15],  # 4 points
                [16, 12, 0, 0],    # 0 points
                [25, 24, 27, 25],  # 2 points
                [0, 0, 45, 0]      # 2 points
            ]                      # 1 points from total score (425)
        )
        self.assertEqual(complete_scoresheet_2.calc_points(), 13)


class PlayerTest(unittest.TestCase):

    def test_username(self) -> None:
        player = b.Player()
        player.init("John", None)

        self.assertEqual(player.username, "John")

    @patch('plugins.balut.Scoresheet')
    def test_settle_score_to_scoresheet(self, mock_scoresheet) -> None:
        mock_scoresheet.select_category_to_settle_score.return_value = 1
        player = b.Player()
        player.init(None, mock_scoresheet)

        hand = [1, 2, 3, 4, 5]
        player.settle_score_to_scoresheet(hand)

        mock_scoresheet.display_with_score.assert_called_once_with(hand)
        mock_scoresheet.select_category_to_settle_score.assert_called_once_with()
        mock_scoresheet.settle_score.assert_called_once_with(1, hand)
        mock_scoresheet.display.assert_called_once_with()

    @patch('plugins.balut.Scoresheet')
    def test_calc_points(self, mock_scoresheet) -> None:
        mock_scoresheet.calc_points.return_value = 9
        player = b.Player()
        player.init(None, mock_scoresheet)

        self.assertEqual(player.calc_points(), 9)

        mock_scoresheet.calc_points.assert_called_once_with()

class BalutTest(unittest.TestCase):
    MIN_DICE = 1
    MAX_DICE = 5

    def setUp(self) -> None:
        self.balut = b.Balut()
        self.balut.init(hand=[2, 3, 3, 4, 5])

    @patch('builtins.print')
    def test_display_instructions(self, mock_print) -> None:
        self.balut.display_instructions()
        mock_print.assert_called_once()

    @patch('builtins.print')
    def test_display_hand(self, mock_print) -> None:
        self.balut.display_hand(username='John')

        calls = [
            call('\nJohn you have rolled:'),
            call('Dice 1 has a face of 2'),
            call('Dice 2 has a face of 3'),
            call('Dice 3 has a face of 3'),
            call('Dice 4 has a face of 4'),
            call('Dice 5 has a face of 5'),
            call()
        ]
        mock_print.assert_has_calls(calls)

    @patch('plugins.balut.random')
    def test_roll_dice(self, mock_random) -> None:
        balut = b.Balut()
        balut.init(hand=[2, 3, 3, 4, 5])
        mock_random.randint.side_effect = [3, 6]

        dice_to_roll = 1
        balut.roll_dice(dice_to_roll)
        self.assertEqual(balut._hand[dice_to_roll - 1], 3)

        dice_to_roll = 3
        balut.roll_dice(dice_to_roll)
        self.assertEqual(balut._hand[dice_to_roll - 1], 6)

        calls = [call(1, 6), call(1, 6)]
        mock_random.randint.assert_has_calls(calls)

    @patch('plugins.balut.Balut.roll_dice')
    def test_roll_all_dices(self, mock_roll_dice) -> None:
        self.balut.roll_all_dices()

        calls = [call(1), call(2), call(3), call(4), call(5)]
        mock_roll_dice.assert_has_calls(calls)

    def test__validate_dice_valid(self) -> None:
        self.assertTrue(self.balut._validate_dice(self.MIN_DICE))
        self.assertTrue(self.balut._validate_dice(self.MAX_DICE))

    def test__validate_dice_invalid(self) -> None:
        with self.assertRaises(b.InvalidDiceValueError) as e:
            self.balut._validate_dice(self.MIN_DICE - 1)

        self.assertEqual(
            str(e.exception),
            'Oops! Dices should be integers between 1 and 5. Try again...\n')


        with self.assertRaises(b.InvalidDiceValueError) as e:
            self.balut._validate_dice(self.MAX_DICE + 1)

        self.assertEqual(
            str(e.exception),
            'Oops! Dices should be integers between 1 and 5. Try again...\n')

    def test__convert_to_dices_to_reroll(self) -> None:
        self.assertEqual(self.balut._convert_to_dices_to_reroll('1'), [1])
        self.assertEqual(self.balut._convert_to_dices_to_reroll('1 2 3'), [1, 2, 3])

        with self.assertRaises(ValueError):
            self.balut._convert_to_dices_to_reroll('txt')

        with self.assertRaises(b.InvalidDiceValueError):
            self.balut._convert_to_dices_to_reroll('-1')

    @patch('builtins.input', return_value='\n')
    def test_reroll_dices_preserve_hand(self, mock_input) -> None:
        with self.assertRaises(b.PreserveHand):
            self.balut.reroll_dices()

        mock_input.assert_called_once_with(
            'Select the dices to reroll seperated by space or press enter to continue: ')

    @patch('plugins.balut.Balut.roll_dice')
    @patch('builtins.print')
    @patch('builtins.input', side_effect=['txt', '-1', '1 2 3'])
    def test_reroll_dices(self, mock_inputs, mock_print, mock_roll_dice) -> None:
        self.balut.reroll_dices()

        roll_dice_calls = [call(1), call(2), call(3)]
        mock_roll_dice.assert_has_calls(roll_dice_calls)

        print_calls = [
            call('Oops! Dices should be integers. Try again...\n'),
            call('Oops! Dices should be integers between 1 and 5. Try again...\n')
        ]
        mock_print.assert_has_calls(print_calls)

        input_calls = [
            call('Select the dices to reroll seperated by space or press enter to continue: '),
            call('Select the dices to reroll seperated by space or press enter to continue: '),
            call('Select the dices to reroll seperated by space or press enter to continue: ')
        ]
        mock_inputs.assert_has_calls(input_calls)

    @patch('plugins.balut.Player')
    @patch('plugins.balut.Balut.display_hand')
    @patch('plugins.balut.Balut.reroll_dices')
    @patch('plugins.balut.Balut.roll_all_dices')
    def test_play_round(self, mock_roll_all_dices, mock_reroll_dices,
            mock_display_hand, mock_player) -> None:
        mock_reroll_dices.side_effect = [None, b.PreserveHand()]

        self.balut.play_round(mock_player)

        mock_roll_all_dices.assert_called_once_with()
        mock_display_hand.assert_has_calls(
            [call(mock_player.username), call(mock_player.username)])
        mock_reroll_dices.assert_has_calls([call(), call()])
        mock_player.settle_score_to_scoresheet.assert_called_once_with(self.balut._hand)

    @patch('builtins.print')
    def test__display_winner_one_winner(self, mock_print) -> None:
        mock_player = Mock(username='John')

        self.balut._display_winner([mock_player])

        mock_print.assert_called_once_with('\nCongratulations John you are the winner!')

    @patch('builtins.print')
    def test__display_winner_more_than_one_winners(self, mock_print) -> None:
        mock_player_1 = Mock(username='John')
        mock_player_2 = Mock(username='Hamid')

        self.balut._display_winner([mock_player_1, mock_player_2])

        calls = [
            call('\nThere is a tie between:', end=''),
            call(' John ', end='&'),
            call(' Hamid ', end='\n')
        ]
        mock_print.assert_has_calls(calls)

    @patch('builtins.print')
    def test_display_results_one_player(self, mock_print) -> None:
        mock_player = Mock(username='John')
        mock_player.calc_points.return_value = 380

        self.balut.display_results([mock_player])

        mock_print.assert_called_once_with("John's total points are: 380")

    @patch('builtins.print')
    def test__display_results_more_than_one_player_with_winner(self,
            mock_print) -> None:
        mock_player_1 = Mock(username='John')
        mock_player_1.calc_points.return_value = 420
        mock_player_2 = Mock(username='Hamid')
        mock_player_2.calc_points.return_value = 380

        self.balut.display_results([mock_player_1, mock_player_2])

        calls = [
            call("John's total points are: 420"),
            call("Hamid's total points are: 380"),
            call('\nCongratulations John you are the winner!')
        ]
        mock_print.assert_has_calls(calls)

    @patch('builtins.print')
    def test__display_results_more_than_one_player_without_winner(self,
            mock_print) -> None:
        mock_player_1 = Mock(username='John')
        mock_player_1.calc_points.return_value = 420
        mock_player_2 = Mock(username='Hamid')
        mock_player_2.calc_points.return_value = 420

        self.balut.display_results([mock_player_1, mock_player_2])

        calls = [
            call("John's total points are: 420"),
            call("Hamid's total points are: 420"),
            call('\nThere is a tie between:', end=''),
            call(' John ', end='&'),
            call(' Hamid ', end='\n')
        ]
        mock_print.assert_has_calls(calls)

    @patch('plugins.balut.Player')
    @patch('plugins.balut.Player')
    @patch('plugins.balut.Balut.play_round')
    @patch('plugins.balut.Balut.display_results')
    @patch('plugins.balut.Balut.display_instructions')
    def test_play(self, mock_display_instructions, mock_display_results,
            mock_play_round, mock_player_1, mock_player_2) -> None:
        players = [mock_player_1, mock_player_2]

        self.balut.play(players)

        mock_display_instructions.assert_called_once_with()
        self.assertEqual(mock_play_round.call_count, 56)
        mock_display_results.assert_called_once_with(players)


class BalutPluginTest(PluginTest):

    def setUp(self):
        self.balut_plugin = self.load_plugin(b.BalutPlugin)

    def test_create_categories(self) -> None:
        fours, fives, sixes, straight, full_house, choice, balut = \
            self.balut_plugin.create_categories()

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

    @patch('builtins.print')
    @patch('builtins.input', side_effect=['txt', '-1', '2'])
    def test_read_num_of_players(self, mock_inputs, mock_print) -> None:
        self.assertEqual(self.balut_plugin.read_num_of_players(), 2)

        print_calls = [
            call('Oops! Invalid number of players. Try again...\n'),
            call('Oops! Invalid number of players. Try again...\n')
        ]
        mock_print.assert_has_calls(print_calls)

        input_calls = [
            call('Number of players: '),
            call('Number of players: '),
            call('Number of players: ')
        ]
        mock_inputs.assert_has_calls(input_calls)

    @patch('builtins.input', side_effect=['John', 'Hamid'])
    def test_read_usernames(self, mock_inputs) -> None:
        num_of_players = 2
        usernames = self.balut_plugin.read_usernames(num_of_players)

        self.assertEqual(len(usernames), num_of_players)

        self.assertEqual(usernames[0], 'John')
        self.assertEqual(usernames[1], 'Hamid')

        input_calls = [
            call('Player 1 username: '),
            call('Player 2 username: ')
        ]
        mock_inputs.assert_has_calls(input_calls)

    def test_create_scoresheets(self) -> None:
        num_of_players = 2
        categories = Mock()
        empty_scoresheet = [
            [-1, -1, -1, -1],
            [-1, -1, -1, -1],
            [-1, -1, -1, -1],
            [-1, -1, -1, -1],
            [-1, -1, -1, -1],
            [-1, -1, -1, -1],
            [-1, -1, -1, -1],
        ]

        scoresheets = self.balut_plugin.create_scoresheets(
            num_of_players, categories)

        self.assertEqual(len(scoresheets), num_of_players)

        self.assertIsInstance(scoresheets[0], b.Scoresheet)
        self.assertEqual(scoresheets[0]._categories, categories)
        self.assertEqual(scoresheets[0]._scoresheet_matrix, empty_scoresheet)

        self.assertIsInstance(scoresheets[1], b.Scoresheet)
        self.assertEqual(scoresheets[1]._categories, categories)
        self.assertEqual(scoresheets[1]._scoresheet_matrix, empty_scoresheet)

    @patch('plugins.balut.Scoresheet')
    @patch('plugins.balut.Scoresheet')
    def test_create_players(self, mock_scoresheet_1, mock_scoresheet_2) -> None:
        num_of_players = 2
        usernames = ['John', 'Hamid']
        scoresheets = [mock_scoresheet_1, mock_scoresheet_2]

        players = self.balut_plugin.create_players(usernames, scoresheets)

        self.assertEqual(len(players), num_of_players)

        self.assertIsInstance(players[0], b.Player)
        self.assertEqual(players[0].username, 'John')
        self.assertEqual(players[0]._scoresheet, mock_scoresheet_1)

        self.assertIsInstance(players[1], b.Player)
        self.assertEqual(players[1].username, 'Hamid')
        self.assertEqual(players[1]._scoresheet, mock_scoresheet_2)
