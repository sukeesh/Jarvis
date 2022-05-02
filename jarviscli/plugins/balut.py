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

    def __call__(self, jarvis, _) -> None:
        categories = self.create_categories()
