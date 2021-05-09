from colorama import Fore
from plugin import plugin


@plugin("bmr")
def bmr(jarvis, s):
    """A Jarvis plugin to calculate
    your Basal  Metabolic Rate (BMR) and
    your Active Metabolic Rate(AMR)"""

    jarvis.say("Hello there! Ready to count your BMR? \n")
    jarvis.say("1. Yes, let's start! \n2. Sorry,"
               " I don't know what BMR is :( \n ")
    jarvis.say("Please enter your choice: ")
    # validate the input for choice
    choice = jarvis.input()
    while True:
        if choice == "1" or choice == "2":
            break
        else:
            jarvis.say("Sorry, invalid input was given. Try again! \n")
            jarvis.say("Please enter your choice: ")
            choice = jarvis.input()

    # print definition of BMR
    if choice == "2":
        jarvis.say("\nBasal Metabolic Rate (BMR)", Fore.GREEN)
        jarvis.say("is the number of calories your body needs"
                   "\nto accomplish its most basic (basal)\n"
                   "life-sustaining functions. \n")
        jarvis.say("Since you know now, let's calculate it! \n")

    # gets inputs and makes the necessary checks
    jarvis.say("What's your gender? (M/F)")
    while True:
        sex = jarvis.input()
        # ignore lower or upper letters
        if sex.upper() == "M" or sex.upper() == "F":
            break
        jarvis.say("Sorry, invalid input was given!"
                   "Please try again. (M/F)")
    jarvis.say("What is your height (cm) ?")
    while True:
        try:
            height = int(jarvis.input())
            if height <= 0:
                raise ValueError
            break
        except ValueError:
            print("Oops! That was no valid number. Try again...")
    jarvis.say("What is your weight (kg) ?")
    while True:
        try:
            weight = int(jarvis.input())
            if weight <= 0:
                raise ValueError
            break
        except ValueError:
            print("Oops! That was no valid number. Try again...")
    jarvis.say("What is your age ?")
    while True:
        try:
            age = int(jarvis.input())
            if age <= 0:
                raise ValueError
            break
        except ValueError:
            print("Oops! That was no valid number. Try again...")

    # formula changes based on sex
    if sex.upper() == 'F':
        bmr = (float(height) * 6.25) + (float(weight) * 9.99) - \
              (float(age) * 4.92) - 116
    elif sex.upper() == 'M':
        bmr = (float(height) * 6.25) + (float(weight) * 9.99) - \
              (float(age) * 4.92) - 5
    jarvis.say("BMR: " + str(bmr), Fore.GREEN)
    jarvis.say("\nNow that you know your BMR,\nwould you like to calculate "
               "your AMR too based on it?\n")
    # print definition of AMR
    jarvis.say("Active Metabolic Rate (AMR)", Fore.GREEN)
    jarvis.say("is the actual amount of calories you burn\n"
               "each day due to physical activities\n"
               "like going to the gym, aerobics\n")
    jarvis.say("Please enter your choice(Y/N): ")
    amr_choice = jarvis.input()
    # choice of calculating the amr or not
    while True:
        if amr_choice.upper() == "Y" or amr_choice.upper() == "N":
            break
        else:
            jarvis.say("Sorry, invalid input was given. Try again! \n")
            jarvis.say("Please enter your choice(Y/N): ")
            amr_choice = jarvis.input()

    if amr_choice.upper() == "N":
        jarvis.say("Okay, bye!", Fore.BLUE)
    else:
        jarvis.say("Please enter your exercise level: \n")
        jarvis.say("1.Low\n2.Average\n3.High\n4.Every Day\n5.Athletic")
        jarvis.say("Please enter your choice: ")
        # input for exercise level
        # based on the above choices
        exercise_level = jarvis.input()
        level_choices = ("1", "2", "3", "4", "5")
        while True:
            if exercise_level in level_choices:
                break
            else:
                jarvis.say("Sorry, invalid input was given. Try again! \n")
                jarvis.say("Please enter your choice: ")
                exercise_level = jarvis.input()

        # calculate the amr
        # depending on the exercise level
        if exercise_level == "1":
            amr = bmr * 1.2
        if exercise_level == "2":
            amr = bmr * 1.375
        if exercise_level == "3":
            amr = bmr * 1.55
        if exercise_level == "4":
            amr = bmr * 1.725
        if exercise_level == "5":
            amr = bmr * 1.9

        jarvis.say("AMR: " + str(amr), Fore.GREEN)
