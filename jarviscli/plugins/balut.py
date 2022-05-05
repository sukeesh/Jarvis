import random
import textwrap
import itertools
import functools
from plugin import plugin
from typing import Callable, List


ScoreCalculator = Callable[[List[int]], int]
PointsCalculator = Callable[[List[int]], int]


def calc_same_face_score(hand: List[int], face: int) -> int:
    '''
    In the same face categories only the occurrences of the specified dice face
    are counted in the score.
    '''
    return face * hand.count(face)


def calc_same_face_points(fields: List[int], face: int) -> int:
    '''
    In the same face categories in order to get the 2 points of the category,
    the total score of the 4 fields in the scoresheet should indicate that there
    was at least 13 occurrences of the specified dice face in the total rolls
    that was settled in that category.
    '''
    SAME_FACE_POINTS = 2
    MIN_REQUIRED_OCCURRENCES = 13

    if sum(fields) >= face * MIN_REQUIRED_OCCURRENCES:
        return SAME_FACE_POINTS
    return 0


def calc_straight_score(hand: List[int]) -> int:
    '''
    In the Straight category the score is equivalent to the sum of all the dice
    faces in the hand, but only if the hand contains either a small or a large
    straight (consecutive dice faces starting from 1 or 2 respectively),
    otherwise the score is 0.
    '''
    small_straight = [1, 2, 3, 4, 5]
    large_straight = [2, 3, 4, 5, 6]

    sorted_hand = sorted(hand)
    if sorted_hand == small_straight or sorted_hand == large_straight:
        return sum(sorted_hand)
    return 0


def calc_straight_points(fields: List[int]) -> int:
    '''
    In the Straight category the in order to get the 4 points of the category
    all of its 4 fields in the scoresheet should contain straights, which is
    equivalent to all of the 4 fields having score.
    '''
    STRAIGHT_POINTS = 4

    if 0 not in fields:
        return STRAIGHT_POINTS
    return 0


def calc_full_house_score(hand: List[int]) -> int:
    '''
    In the Full House category the score is equivalent to the sum of all the dice
    faces in the hand, but only if the hand contains a full house (two of a kind
    & three of a kind), otherwise the score is 0.
    '''
    TWO_OF_A_KIND = 2
    THREE_OF_A_KIND = 3

    face_counts = [hand.count(i + 1) for i in range(6)]
    if TWO_OF_A_KIND in face_counts and THREE_OF_A_KIND in face_counts:
        return sum(hand)
    return 0


def calc_full_house_points(fields: List[int]) -> int:
    '''
    In the Full House category in order to get the 3 points of the category
    all of its 4 fields in the scoresheet should contain full houses, which
    is equivalent to all of the 4 fields having score.
    '''
    FULL_HOUSE_POINTS = 3

    if 0 not in fields:
        return FULL_HOUSE_POINTS
    return 0


def calc_choice_score(hand: List[int]) -> int:
    '''
    In the Choice category the score is equivalent to the sum of all the dice faces
    in the hand.
    '''
    return sum(hand)


def calc_choice_points(fields: List[int]) -> int:
    '''
    In the Choice category in order to get the 2 points of the category is
    the total score of the 4 fields in the scoresheet should be greater than
    or equal to 100.
    '''
    CHOICE_POINTS = 2
    MIN_REQUIRED_SCORE = 100

    if sum(fields) >= MIN_REQUIRED_SCORE:
        return CHOICE_POINTS
    return 0


def calc_balut_score(hand: List[int]) -> int:
    '''
    In the Balut category the score is equivalent to the sum of all the dice
    faces in the hand plus 20, but only if the hand contains a Balut (five of
    a kind), otherwise the score is 0.
    '''
    BALUT_BASE_SCORE = 20

    if len(set(hand)) == 1:
        return BALUT_BASE_SCORE + sum(hand)
    return 0


def calc_balut_points(fields: List[int]) -> int:
    '''
    In the Balut category you get 2 points for every Balut that is settled in
    any of its 4 fields in the scoresheet, which equivalent to a field contain
    score not equal to 0.
    '''
    POINTS_PER_BALUT = 2

    return sum([POINTS_PER_BALUT for field in fields if field != 0])


class Category:

    def init(self, label: str, score_calculator: ScoreCalculator,
            points_calculator: PointsCalculator) -> None:
        self._label = label
        self._score_calculator = score_calculator
        self._points_calculator = points_calculator

    @property
    def label(self) -> str:
        return self._label

    @property
    def calc_score(self) -> ScoreCalculator:
        return self._score_calculator

    @property
    def calc_points(self) -> PointsCalculator:
        return self._points_calculator


class InvalidCategoryValueError(ValueError):
    pass


class Scoresheet:
    NUM_OF_FIELDS = 4
    NUM_OF_CATEGORIES = 7
    EMPTY_FIELD_PLACEHOLDER = -1

    def init(self, categories: List[Category],
            scoresheet_matrix: List[List[int]]) -> None:
        self._categories = categories
        self._scoresheet_matrix = scoresheet_matrix

    def _validate_category(self, category: int) -> bool:
        if not(1 <= category <= self.NUM_OF_CATEGORIES):
            raise InvalidCategoryValueError(
                'Oops! Category should be an integer between 1 and 7. Try again...\n')

        if self.EMPTY_FIELD_PLACEHOLDER not in self._scoresheet_matrix[category - 1]:
            raise InvalidCategoryValueError(
                'Oops! The category you selected is already full. Try again...\n')

        return True

    def select_category_to_settle_score(self) -> int:
        while True:
            try:
                category = \
                    int(input('Select the category to settle the score (1-7): '))

                if self._validate_category(category):
                    return category
            except InvalidCategoryValueError as error:
                print(str(error))
            except ValueError:
                print('Oops! Category should be an integer. Try again...\n')

    def _find_first_empty_field(self, category: int) -> int:
        for field, field_score in enumerate(self._scoresheet_matrix[category - 1]):
            if field_score == self.EMPTY_FIELD_PLACEHOLDER:
                return field

    def _settle_score_to_field(self, category: int, field: int, hand: List[int]) -> None:
        self._scoresheet_matrix[category - 1][field] = \
            self._categories[category - 1].calc_score(hand)

    def settle_score(self, category: int, hand: List[int]) -> None:
        field = self._find_first_empty_field(category)
        self._settle_score_to_field(category, field, hand)

    def display(self) -> None:
        print('\n===================== Scoresheet =====================')
        print(f"{'': <3}{'Category': <12}{'Field 1': ^10}"
              f"{'Field 2': ^10}{'Field 3': ^10}{'Field 4': ^10}")

        for i, (field_1, field_2, field_3, field_4) in enumerate(self._scoresheet_matrix):
            field_1 = '-' if field_1 == -1 else field_1
            field_2 = '-' if field_2 == -1 else field_2
            field_3 = '-' if field_3 == -1 else field_3
            field_4 = '-' if field_4 == -1 else field_4

            print(f"{i+1: <3}{self._categories[i].label: <12}{field_1: ^10}"
                  f"{field_2: ^10}{field_3: ^10}{field_4: ^10}")

        print('======================================================\n')

    def display_with_score(self, hand: List[int]) -> None:
        print('\n=========================== Scoresheet ===========================')
        print(f"{'': <3}{'Category': <12}{'Field 1': ^10}"
              f"{'Field 2': ^10}{'Field 3': ^10}{'Field 4': ^10}{'Score Gain': ^10}")

        for i, (field_1, field_2, field_3, field_4) in enumerate(self._scoresheet_matrix):
            field_1 = '-' if field_1 == -1 else field_1
            field_2 = '-' if field_2 == -1 else field_2
            field_3 = '-' if field_3 == -1 else field_3
            field_4 = '-' if field_4 == -1 else field_4

            if field_4 == '-':
                score_gain = f"+{self._categories[i].calc_score(hand)}"
            else:
                score_gain = 'Full'

            print(f"{i+1: <3}{self._categories[i].label: <12}{field_1: ^10}"
                  f"{field_2: ^10}{field_3: ^10}{field_4: ^10}{score_gain: ^10}")

        print('==================================================================\n')

    def _calc_total_score_points(self, total_score: int) -> int:
        if 0 <= total_score <= 299:
            return -2
        elif 300 <= total_score <= 349:
            return -1
        elif 350 <= total_score <= 399:
            return 0
        elif 400 <= total_score <= 449:
            return 1
        elif 450 <= total_score <= 499:
            return 2
        elif 500 <= total_score <= 549:
            return 3
        elif 550 <= total_score <= 599:
            return 4
        elif 600 <= total_score <= 649:
            return 5
        elif 650 <= total_score <= 812:
            return 6

    def calc_points(self) -> int:
        total_score = 0
        total_points = 0
        for category, fields in enumerate(self._scoresheet_matrix):
            total_score += sum(fields)
            total_points += self._categories[category].calc_points(fields)

        total_points += self._calc_total_score_points(total_score)

        return total_points


class Player:

    def init(self, username: str, scoresheet: Scoresheet) -> None:
        self._username = username
        self._scoresheet = scoresheet

    @property
    def username(self) -> str:
        return self._username

    def settle_score_to_scoresheet(self, hand: List[int]) -> None:
        self._scoresheet.display_with_score(hand)
        category = self._scoresheet.select_category_to_settle_score()
        self._scoresheet.settle_score(category, hand)
        self._scoresheet.display()

    def calc_points(self) -> int:
        return self._scoresheet.calc_points()


class InvalidDiceValueError(ValueError):
    pass


class PreserveHand(Exception):
    pass


class Balut:
    NUM_OF_DICES = 5
    NUM_OF_ROUNDS = 28

    def init(self, hand: List[int]) -> None:
        self._hand = hand

    def display_instructions(self) -> None:
        instructions = textwrap.dedent(f"""
        =========================== Instructions ===========================
        Balut is a dice game that consists of 28 rounds. In each round you
        can roll the dices up to 3 times and then you have to enter your
        roll in one of the 7 categories on the scoresheet. You must fill 4
        fields in each category. Once a field is settled it cannot be changed
        for the rest of the game. Each category has some requirements, that
        if they are satisfied you receive the points of the category.
        The object of the game is to maximize your number of points.

        Categories:
        1) Fours: The score for this category is the sum of 4 in your hand.
        2) Fives: The score for this category is the sum of 5 in your hand.
        3) Sixes: The score for this category is the sum of 6 in your hand.
        4) Straight: The score for this category is the sum of all the dice
           faces in your hand if the dice faces are consecutive (straight),
           otherwise it is zero.
        5) Full House: The score for this category is the sum of all the dice
           faces in your hand if you have both three of a kind and a pair (full
           house), otherwise it is zero.
        6) Choice: The score for this category is the sum of all the dice faces
           in your hand.
        7) Balut: The score for this category is 20 plus the sum of all the dice
           faces in your hand if you have five of a kind, otherwise it is zero.


        {'CATEGORY': <14}{'REQUIREMENTS': <18}{'POINTS AWARDED': ^14}
        {'Fours': <14}{'Score >= 52': <18}{'2': ^14}
        {'Fives': <14}{'Score >= 65': <18}{'2': ^14}
        {'Sixes': <14}{'Score >= 78': <18}{'2': ^14}
        {'Straight': <14}{'All Straights': <18}{'4': ^14}
        {'Full House': <14}{'All Full Houses': <18}{'3': ^14}
        {'Choice': <14}{'Score >= 100': <18}{'2': ^14}
        {'Balut': <14}{'For each Balut': <18}{'2': ^14}

        {'TOTAL SCORE': <14}{'POINTS AWARDED': ^14}
        {'0-299': ^12}{'-2': ^16}
        {'300-349': ^12}{'-1': ^16}
        {'350-399': ^12}{'0': ^17}
        {'400-449': ^12}{'1': ^17}
        {'450-499': ^12}{'2': ^17}
        {'500-549': ^12}{'3': ^17}
        {'550-599': ^12}{'4': ^17}
        {'600-649': ^12}{'5': ^17}
        {'650-812': ^12}{'6': ^17}
        ====================================================================
        """)

        print(instructions)

    def display_hand(self, username: str) -> None:
        print(f'\n{username} you have rolled:')
        for i, face in enumerate(self._hand):
            print(f'Dice {i + 1} has a face of {face}')
        print()

    def roll_dice(self, dice_to_roll: int) -> None:
        self._hand[dice_to_roll - 1] = random.randint(1, 6)

    def roll_all_dices(self) -> None:
        for dice, _ in enumerate(self._hand, start=1):
            self.roll_dice(dice)

    def _validate_dice(self, dice: int) -> bool:
        if not(1 <= dice <= self.NUM_OF_DICES):
            raise InvalidDiceValueError(
                'Oops! Dices should be integers between 1 and 5. Try again...\n')
        return True

    def _convert_to_dices_to_reroll(self, selected_dices: str) -> List[int]:
        return [int(dice) for dice in selected_dices.split(' ')
                if self._validate_dice(int(dice))]

    def reroll_dices(self) -> None:
        while True:
            try:
                selected_dices = input(
                    'Select the dices to reroll seperated by space or press enter '
                    'to continue: '
                ).strip()

                if selected_dices == '':  # User pressed enter
                    raise PreserveHand()

                dices_to_reroll = self._convert_to_dices_to_reroll(selected_dices)

                for dice_to_roll in dices_to_reroll:
                    self.roll_dice(dice_to_roll)
                return
            except InvalidDiceValueError as error:
                print(str(error))
            except ValueError as error:
                print('Oops! Dices should be integers. Try again...\n')

    def play_round(self, player: Player) -> None:
        self.roll_all_dices()
        self.display_hand(player.username)

        rerolls = 0
        while rerolls < 2:
            try:
                self.reroll_dices()
                self.display_hand(player.username)
                rerolls += 1
            except PreserveHand:
                break

        player.settle_score_to_scoresheet(self._hand)

    def _display_winner(self, max_players: List[Player]) -> None:
        if len(max_players) == 1:
            print(f"\nCongratulations {max_players[0].username} you are the winner!")
        elif len(max_players) > 1:
            print(f'\nThere is a tie between:', end='')
            for i, player in enumerate(max_players, start=1):
                end_value = '&' if i != len(max_players) else '\n'
                print(f' {player.username} ', end=end_value)

    def display_results(self, players: List[Player]) -> None:
        max_points = float('-inf')
        max_players = []
        for player in players:
            player_points = player.calc_points()
            print(f"{player.username}'s total points are: {player_points}")

            if player_points > max_points:
                max_points = player_points
                max_players = [player]
            elif player_points == max_points:
                max_players.append(player)

        if len(players) > 1:
            self._display_winner(max_players)

    def play(self, players: List[Player]) -> None:
        self.display_instructions()

        players_cycle = itertools.cycle(players)
        for _ in range(len(players) * self.NUM_OF_ROUNDS):
            player = next(players_cycle)
            self.play_round(player)

        self.display_results(players)


@plugin("balut")
class BalutPlugin:

    def create_categories(self) -> List[Category]:
        fours = Category()
        fours.init("Fours",
            functools.partial(calc_same_face_score, face=4),
            functools.partial(calc_same_face_points, face=4))

        fives = Category()
        fives.init("Fives",
            functools.partial(calc_same_face_score, face=5),
            functools.partial(calc_same_face_points, face=5))

        sixes = Category()
        sixes.init("Sixes",
            functools.partial(calc_same_face_score, face=6),
            functools.partial(calc_same_face_points, face=6))

        straight = Category()
        straight.init("Straight", calc_straight_score, calc_straight_points)

        full_house = Category()
        full_house.init("Full House", calc_full_house_score, calc_full_house_points)

        choice = Category()
        choice.init("Choice", calc_choice_score, calc_choice_points)

        balut = Category()
        balut.init("Balut", calc_balut_score, calc_balut_points)

        return [fours, fives, sixes, straight, full_house, choice, balut]

    def read_num_of_players(self) -> int:
        while True:
            try:
                num_of_players = int(input('Number of players: '))
                if num_of_players <= 0:
                    raise ValueError()
                return num_of_players
            except ValueError:
                print('Oops! Invalid number of players. Try again...\n')

    def read_usernames(self, num_of_players: int) -> List[str]:
        usernames = []
        for i in range(num_of_players):
            username = input(f'Player {i+1} username: ')
            usernames.append(username)
        return usernames

    def create_scoresheets(self, num_of_players: int,
            categories: List[Category]) -> List[Scoresheet]:
        scoresheets = []
        for _ in range(num_of_players):
            scoresheet = Scoresheet()
            scoresheet_matrix = [
                [Scoresheet.EMPTY_FIELD_PLACEHOLDER for _ in range(Scoresheet.NUM_OF_FIELDS)]
                for _ in range(Scoresheet.NUM_OF_CATEGORIES)
            ]
            scoresheet.init(categories, scoresheet_matrix)
            scoresheets.append(scoresheet)
        return scoresheets

    def create_players(self, usernames: List[str],
            scoresheets: List[Scoresheet]) -> List[Player]:
        players = []
        for username, scoresheet in zip(usernames, scoresheets):
            player = Player()
            player.init(username, scoresheet)
            players.append(player)
        return players

    def __call__(self, jarvis, _) -> None:
        num_of_players = self.read_num_of_players()
        usernames = self.read_usernames(num_of_players)
        categories = self.create_categories()
        scoresheets = self.create_scoresheets(num_of_players, categories)
        players = self.create_players(usernames, scoresheets)

        balut = Balut()
        balut.init(hand=[-1 for _ in range(Balut.NUM_OF_DICES)])
        balut.play(players)
