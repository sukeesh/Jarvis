from plugin import plugin
from colorama import Fore, Back, Style


@plugin('bmi')
class Bmi:
    """
    Welcome to the Body Mass Index plugin documentation! Here you can find all the functionalitites
    of this plugin.
    Usage: Type bmi, press enter and follow the instructions
    Functionalities: You can calculate your BMI both on metric and imperial system.
    For metric system: Type your height in centimetres and the your weight in kilos,
        they should be both Integers!
    For imperial system: Type your height in feets and inches and then your weight in lbs
        all measurements should be Integers!
    Find out your BMI number and your body state.
    """

    def __call__(self, jarvis, s):
        jarvis.say("Welcome. Lets check your BMI")
        system = self.get_system(jarvis)
        if system == 'metric':
            bmi = self.calc_bmi('m', *self.ask_measurements(jarvis, "m"))
        elif system == 'imperial':
            bmi = self.calc_bmi('i', *self.ask_measurements(jarvis, "i"))
        else:
            return
        self.print_body_state(jarvis, bmi)

    def get_system(self, jarvis):
        """
        Asks for the user to choose which system he wants to use
        1 for metric and 2 for imperial
        """
        syst = {1: 'metric', 2: 'imperial'}
        jarvis.say("Metric system: Type your height in centimeter, weight in kg")
        jarvis.say("Imperial system: Type your height in ft and inches, weight in lbs")
        jarvis.say("All measurements should be Integers. Default is Metric system")
        print()
        prompt = "Please choose the system you would like to use. \n 1: Metric system \n 2: Imperial system \n 3: Exit"
        valid_input = False
        while not valid_input:
            try:
                print(prompt)
                c = int(input("Your choice: "))
                print()
                if c != 3:
                    return syst.get(c, 'metric')
                valid_input = True
            except ValueError:
                print("Invalid Input. Please Enter the number")

    def calc_bmi(self, system, height, weight):
        """
        Calculates the bmi for metric system using the common bmi function
        """
        if system == 'm':
            height = height / 100.0
            bmi = 1.0 * weight / height ** 2
        elif system == 'i':
            bmi = 1.0 * weight / height ** 2 * 703
        bmi = round(bmi, 1)
        return bmi

    def print_body_state(self, jarvis, bmi):
        """
        According the bmi number, print_body_state finds out the state of the body
        and prints it to the user using colorama library for some coloring
        """
        print("BMI:", str(bmi))
        if bmi < 16:
            print(Back.RED, " " * 2, Style.RESET_ALL)
            jarvis.say('Severe thinness')
        elif bmi < 18.5:
            print(Back.YELLOW, " " * 2, Style.RESET_ALL)
            jarvis.say('Mild thinness')
        elif bmi < 25:
            print(Back.GREEN, " " * 2, Style.RESET_ALL)
            jarvis.say('Healthy')
        elif bmi < 30:
            print(Back.YELLOW, " " * 2, Style.RESET_ALL)
            jarvis.say('Pre-obese')
        else:
            print(Back.RED, " " * 2, Style.RESET_ALL)
            jarvis.say('Obese')

    def ask_measurements(self, jarvis, s):
        """
        Asks user to imput his measurements according the system he is using.
        If the user doesn't input an Integer, jarvis will ask him to insert value again.
        """
        if s == "m":
            jarvis.say("Please insert your height in centimeter: ")
            height = jarvis.input()
            while True:
                try:
                    height = int(height)
                    if height < 0:
                        raise ValueError('Please only positive numbers')
                    break
                except ValueError:
                    print("Error on input type for height, please insert an integer: ")
                    height = jarvis.input()
            jarvis.say("Please insert your weight in kg: ")
            weight = jarvis.input()
            while True:
                try:
                    weight = int(weight)
                    if weight <= 0:
                        raise ValueError('Please only positive numbers')
                    break
                except ValueError:
                    print("Error on input type for weight, please insert an integer: ")
                    weight = jarvis.input()
        else:
            jarvis.say("Please insert your height in ft: ")
            feet = jarvis.input()
            while True:
                try:
                    feet = int(feet)
                    if feet < 0:
                        raise ValueError('Please only positive numbers!')
                    break
                except ValueError:
                    print("Error on input type for feet, please insert an integer: ")
                    feet = jarvis.input()
            jarvis.say("Please insert your height in inches: ")
            inches = jarvis.input()
            while True:
                try:
                    inches = int(inches)
                    if inches < 0:
                        raise ValueError('Please only positive numbers')
                    break
                except ValueError:
                    print("Error on input type for inches, please insert an integer: ")
                    inches = jarvis.input()
            jarvis.say("Please insert your weight in lbs: ")
            weight = jarvis.input()
            while True:
                try:
                    weight = int(weight)
                    if weight < 0:
                        raise ValueError('Please only positive numbers')
                    break
                except ValueError:
                    print("Error on input type for weight, please insert an integer: ")
                    weight = jarvis.input()
            height = int(feet) * 12 + int(inches)
            weight = int(weight)
        return height, weight
