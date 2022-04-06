from colorama import Fore
from plugin import plugin, alias
from typing import Callable, Tuple


class ValueOutOfRangeError(Exception):
    pass


@alias("macros")
@plugin("calories")
class CaloriesMacrosPlugin:
    """
    calculates recommended daily calorie
    intake,calories for weight add and loss.
    The calculating method is based on gender, age, height and weight.
    since it uses the Miffin-St Jeor Equation as it is considered the
    most accurate when we don't know our body fat percentage(Source 2).
    Add gender(man/woman), age(15 - 80 recommended), metric height(cm),
    weight(kg), workout level(1-4). No decimal weight for now.
    Workout Levels:
        [1] Little or no exercise
        [2] Light 1-3 per week
        [3] Moderate 4-5 per week
        [4] Active daily exercise or physical job
    #Example: health calories woman 27 164 60 3
    ^Sources:
            1) https://en.wikipedia.org/wiki/Basal_metabolic_rate
            2) https://jandonline.org/article/S0002-8223(05)00149-5/fulltext
    """

    def __call__(self, jarvis, _) -> None:
        """
        Calls the needed methods to validate the values that need to be parsed
        as arguments to calories method. Afterwards, the last mentioned method
        is called in order to calculate the calorie intake data.
        """
        self.display_welcome_message(jarvis)

        input_msg = 'Gender (M/F): '
        error_msg = 'Oops! That was not a valid gender. Please try again (M/F)...'
        gender = self.read_gender(jarvis, input_msg, error_msg)

        input_msg = 'Age: '
        bool_expression: Callable[[int], bool] = lambda age: age < 14
        error_msg = ('We suggest you to consult a nutrition expert if you are '
            'under 14 years old.'
            '\nIf you made a mistake while entering your age, try again...')
        age = self.read_input(jarvis, input_msg, bool_expression, error_msg)

        input_msg = 'Height (cm): '
        bool_expression: Callable[[int], bool] = lambda height: height <= 0
        error_msg = 'Oops! That was not a valid height. Try again...'
        height = self.read_input(jarvis, input_msg, bool_expression, error_msg)

        input_msg = 'Weight (kg): '
        bool_expression: Callable[[int], bool] = lambda weight: weight <= 0
        error_msg = 'Oops! That was not a valid weight. Try again...'
        weight = self.read_input(jarvis, input_msg, bool_expression, error_msg)

        self.display_activity_levels(jarvis)
        input_msg = 'Choose your activity level (1-4): '
        bool_expression: Callable[[int], bool] = \
            lambda activity_level: not(1 <= activity_level <= 4)
        error_msg = 'Oops! Invalid input. Try again (1-4)...'
        activity_level = self.read_input(
            jarvis, input_msg, bool_expression, error_msg)

        brm_info = self.calories(gender, age, height, weight, activity_level)
        self.display_results(jarvis, brm_info)

    def yellow(self, content: str) -> str:
        return f'{Fore.YELLOW}{content}{Fore.RESET}'

    def red(self, content: str) -> str:
        return f'{Fore.RED}{content}{Fore.RESET}'

    def display_welcome_message(self, jarvis) -> None:
        jarvis.say(self.yellow(
            '\nHello! In order to calculate your daily calorie intake '
            'i will need some information about you. Lets start...'))

    def display_activity_levels(self, jarvis) -> None:
        jarvis.say(self.yellow("\nActivity levels:"))
        jarvis.say(f'{self.yellow("[1]")} Little or no exercise')
        jarvis.say(f'{self.yellow("[2]")} Light exercise 1-3 days a week')
        jarvis.say(f'{self.yellow("[3]")} Moderate exercise 4-5 days a week')
        jarvis.say(f'{self.yellow("[4]")} Hard exercise every day\n')

    def display_results(self, jarvis, brm_info: Tuple[float, float, float]) -> None:
        jarvis.say(f'{Fore.CYAN}\nYour personal calorie data!')
        jarvis.say(f'Maintain weight calories: {Fore.GREEN}{brm_info[0]}')
        jarvis.say(f'Lose weight calories:     {Fore.YELLOW}{brm_info[1]}')
        jarvis.say(f'Gain weight calories:     {Fore.RED}{brm_info[2]}')

    def read_gender(self, jarvis, input_message: str, error_message: str) -> str:
        while True:
            gender = jarvis.input(input_message)
            if self.validate_gender(gender):
                return gender.upper()
            print(self.red(error_message))

    def validate_gender(self, gender: str) -> bool:
        return (gender.upper() == "M" or gender.upper() == "F")

    def read_input(self, jarvis, input_message: str,
            bool_expression: Callable[[int], bool], error_message: str) -> int:
        while True:
            input = jarvis.input(input_message)
            if self.validate_input(input, bool_expression):
                return int(input)
            print(self.red(error_message))

    def validate_input(self, input: str,
            bool_expression: Callable[[int], bool]) -> bool:
        try:
            input = int(input)
            if bool_expression(input):
                raise ValueOutOfRangeError
            return True
        except (ValueError, ValueOutOfRangeError):
            return False

    def calories(self, gender: str, age: int, height: int, weight: int,
            workout_level: int) -> Tuple[float, float, float]:
        """
        Given the gender, age, height, weight and workout level arguments
        the daily calorie intake is calculated based on the
        Miffin-St Jeor Equation above mentioned method.
        Three specialized rates of daily calorie intake are calculated:
        the intake that preserves one's weight, the one to lose weight
        and the intake to gain more weight.
        """
        if gender.lower == "m":
            gender_no = 5
        else:
            # A constant value based on gender
            gender_no = -161
        brm = float(10 * weight + 6.25 * height - 5
                    * age + gender_no) * self.exercise_level(workout_level)
        # The calculation of the intake to lose weight
        brm_loss = brm - 500.0
        # The calculation of the intake to gain weight
        brm_put_on = brm + 500.0
        return brm, brm_loss, brm_put_on

    def exercise_level(self, level: int) -> float:
        """
        Implements needed calculations for the calorie intake
        calculation method based on the workout level
        """
        multipliers = {1: 1.2, 2: 1.4, 3: 1.6, 4: 1.95}
        multiplier = multipliers.get(level, 1)
        return multiplier
