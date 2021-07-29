from colorama import Fore
from plugin import plugin


@plugin("calories")
class calories:
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

    def __call__(self, jarvis, s):
        """
        Calls the needed methods to validate the values that need to be parsed
        as arguments to calories method. Afterwards, the last mentioned method
        is called in order to calculate the calorie intake data.
        """
        jarvis.say("Hello there! To calculate your daily calorie intake "
                   "I need to get to know you a bit more...")
        gender = jarvis.input("What's your gender? (M/F) ")
        while not self.validate_gender(gender):
            print(Fore.YELLOW + "Sorry, invalid input was given! Please"
                                " try again. (M/F) ")
            gender = jarvis.input()
        # Reads the input age and calls the validation method.
        age = jarvis.input("What's your age? ")
        while not self.validate_age(age):
            age = jarvis.input()
        age = int(age)
        height = jarvis.input("What is your height? (cm) ")
        while not self.validate_height(height):
            height = jarvis.input()
        height = int(height)

        weight = jarvis.input("What is your weight? (kg) ")
        while not self.validate_weight(weight):
            weight = jarvis.input()
        weight = int(weight)
        jarvis.say("Choose your workout level (1-4) ")
        message = Fore.RESET + Fore.YELLOW + "\nWorkout Levels:\n[1]" + \
            Fore.RESET + " Little or no exercise\n"
        message += Fore.RESET + Fore.YELLOW + "[2]" + Fore.RESET + \
            " Light 1-3 per week\n"
        message += Fore.RESET + Fore.YELLOW + "[3]" + Fore.RESET + \
            " Moderate 4-5 per week\n"
        message += Fore.RESET + Fore.YELLOW + "[4]" + \
            Fore.RESET + " Active daily exercise or physical job"
        jarvis.say(message)
        # Reads the input workout_level and calls the validation method.
        workout_level = jarvis.input("Please enter your choice: ")
        while not self.validate_workout_level(workout_level):
            workout_level = jarvis.input()
        workout_level = int(workout_level)

        brm_info = self.calories(gender, age, height, weight, workout_level)
        jarvis.say("\nYour personal calorie data!", Fore.CYAN)
        jarvis.say("Daily calorie intake:    " + Fore.RESET +
                   Fore.GREEN + str(brm_info[0]))
        jarvis.say("Loss weight calories:    " + Fore.RESET +
                   Fore.YELLOW + str(brm_info[1]))
        jarvis.say("Put on  weight calories: " + Fore.RESET +
                   Fore.RED + str(brm_info[2]))

    def validate_gender(self, gender):
        """Function that takes as input the gender and validates it."""
        # ignore lower or upper letters
        return (gender.upper() == "M" or gender.upper() == "F")

    def validate_age(self, age):
        """Function that takes as input the age and validates it."""
        try:
            age = int(age)
            if age <= 0 or age < 14:
                raise ValueError
            else:
                return True
        except ValueError:
            print(Fore.YELLOW + "Oops! That was no valid number."
                                " Try again...")
            return False

    def validate_height(self, height):
        """Function that takes as input the height and validates it."""
        try:
            height = int(height)
            if height <= 0:
                raise ValueError
            else:
                return True
        except ValueError:
            print(Fore.YELLOW + "Oops! That was no valid input."
                                " Try again...")
            return False

    def validate_weight(self, weight):
        """Function that takes as input the weight and validates it."""
        try:
            weight = int(weight)
            if weight <= 0:
                raise ValueError
            else:
                return True
        except ValueError:
            print(Fore.YELLOW + "Oops! That was no valid input. Try again...")
            return False

    def validate_workout_level(self, workout_level):
        """Function that takes as input the workout level and validates it."""
        try:
            workout_level = int(workout_level)
            if workout_level <= 0 or workout_level > 4:
                raise ValueError
            else:
                return True
        except ValueError:
            print(Fore.YELLOW + "Oops! That was no valid input. Try again...")
            return False

    def calories(self, gender, age, height, weight, workout_level):
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

    def exercise_level(self, level):
        """
        Implements needed calculations for the calorie intake
        calculation method based on the workout level
        """
        multipliers = {1: 1.2, 2: 1.4, 3: 1.6, 4: 1.95}
        multiplier = multipliers.get(level, 1)
        return multiplier
