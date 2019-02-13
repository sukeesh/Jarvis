from plugin import plugin
import os
import sys

from colorama import Fore, Back, Style


@plugin('bmi')
class Bmi():
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

        syst = ['metric', 'imperial']
        system = self.get_system('Type your system', syst)

        if system == 'metric':
            height, weight = self.ask_measurements(jarvis, "m")
            calc = self.calc_bmi_m(jarvis, height, weight)
        else:
            height, weight = self.ask_measurements(jarvis, "i")
            calc = self.calc_bmi_i(jarvis, height, weight)

        calc = round(calc, 1)
        print("BMI: ", str(calc))
        self.find_body_state(jarvis, calc)

    def get_system(self, jarvis, syst):
        """
        get_system asks for the user to choose which system he wants to use
        1 for metric and 2 for imperial
        """

        prompt = ('Please choose the system you would like to use\n'
                  '(1) For metric system\n'
                  '(2) For imperial system\n'
                  'Your choice: ')
        while True:
            c = jarvis.input(prompt)
            if c == '1':
                return 'metric'
            elif c == '2':
                return 'imperial'
            elif c == 'help me':
                prompt = (
                    'If you want to calculate on metric system type 1\n'
                    'If you want to calculate on imperial system type 2: ')
                continue
            elif c == 'try again':
                prompt = 'Please type 1 for metric and 2 for imperial system: '
                continue
            else:
                prompt = ('Type <help me> to see valid inputs \n'
                          'or <try again> to continue: ')

    def calc_bmi_m(self, jarvis, height, weight):
        """
        calc_bmi_m calculates the bmi for metric system using the common bmi function
        """

        height = height / 100.0
        bmi = 1.0 * weight / height ** 2
        return bmi

    def calc_bmi_i(self, jarvis, height, weight):
        """
        calc_bmi_i calculates the bmi for imperial system using the common bmi function
        """

        bmi = 1.0 * weight / height ** 2 * 703
        return bmi

    def find_body_state(self, jarvis, calc):
        """
        According the bmi number, find_body_state finds out the state of the body
        and prints it to the user using colorama library for some coloring
        """

        if calc < 16:
            print('STATE: ' + Back.RED + 'Severe thinness')
        elif calc < 18.5:
            print('STATE: ' + Back.YELLOW + 'Mild thinness')
        elif calc < 25:
            print('STATE: ' + Back.GREEN + 'Healthy')
        elif calc < 30:
            print('STATE: ' + Back.YELLOW + 'Pre-obese')
        else:
            print('STATE: ' + Back.RED + 'Obese')
        print(Style.RESET_ALL)

    def ask_measurements(self, jarvis, s):
        """
        ask_meeasurememts asks user to imput his measurements according the system he is using.
        If the user doesn't input an Integer, jarvis will ask him to insert value again.
        """

        if s == "m":
            jarvis.say("Please insert your height (cm): ")
            height = jarvis.input()
            while True:
                try:
                    height = int(height)
                    if height < 0:
                        raise ValueError('Please only positive numbers!')
                    break
                except ValueError:
                    print("Error on input type for height, please insert an integer: ")
                    height = jarvis.input()

            jarvis.say("Please insert your weight (kg): ")
            weight = jarvis.input()
            while True:
                try:
                    weight = int(weight)
                    if weight <= 0:
                        raise ValueError('Please only positive numbers!')
                    break
                except ValueError:
                    print("Error on input type for weight, please insert an integer: ")
                    weight = jarvis.input()

        else:
            jarvis.say("Please insert your height (feet): ")
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

            jarvis.say("Please insert your height (inches): ")
            inches = jarvis.input()
            while True:
                try:
                    inches = int(inches)
                    if inches < 0:
                        raise ValueError('Please only positive numbers!')
                    break
                except ValueError:
                    print("Error on input type for inches, please insert an integer: ")
                    inches = jarvis.input()
            jarvis.say("Please insert your weight (lbs): ")
            weight = jarvis.input()
            while True:
                try:
                    weight = int(weight)
                    if weight < 0:
                        raise ValueError('Please only positive numbers!')
                    break
                except ValueError:
                    print("Error on input type for weight, please insert an integer: ")
                    weight = jarvis.input()

            height = int(feet) * 12 + int(inches)
            weight = int(weight)

        return height, weight
