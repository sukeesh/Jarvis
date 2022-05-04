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

    @property
    def scoresheet(self) -> Scoresheet:
        return self._scoresheet


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
