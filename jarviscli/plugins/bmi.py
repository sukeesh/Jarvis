import os
import sys

from plugin import plugin
from six.moves import input

@plugin('bmi')

class Bmi():

    def __call__(self, jarvis, s):
        syst = ['metric', 'imperial']
        system = self.get_system('Type your system', syst)

        if system == 'metric':
            height, weight = self.ask_measurements(jarvis, "m")
            calc = self.calc_bmi_m(jarvis, height, weight)
        else:
            height, weight = self.ask_measurements(jarvis, "i")
            calc = self.calc_bmi_i(jarvis, height, weight)

        state = self.find_body_state(jarvis, calc)

        calc = round(calc, 1)
        print(str(calc), " ", state)

    def get_system(self, jarvis, syst):

        prompt = 'Please type m for metric and i for imperial system: '
        while True:            
            c= input(prompt)
            if c == 'm':
                return 'metric'
            elif c == 'i':
                return 'imperial'
            elif c == 'help me':
                prompt = ('If you want to calculate on metric system type m\n'
                        'If you want to calculate on imperial system type i: ')
                continue
            elif c == 'try again':
                prompt = 'Please type m for metric and i for imperial system: '
                continue 
            else:
                prompt = 'Type <help me> to see valid inputs '\
                        'or <try again> to continue: '

    def calc_bmi_m(self, jarvis, height, weight):

        #Calculate bmi
        height = height/100
        bmi = weight/height**2
        return bmi

    def calc_bmi_i(self, jarvis, height, weight):

        bmi = weight/height**2 * 703
        return bmi

    def find_body_state(self, jarvis, calc):

        if calc < 18.5:
            state = "Underweight"
        elif calc < 24.9:
            state = "Healthy"
        elif calc < 30:
            state = "Overweight"
        else:
            state = "Obese"

        return state

    def ask_measurements(self, jarvis, s):

        if s == "m":   
            jarvis.say("Please insert your height (cm): ")
            height = input()
            jarvis.say("Please insert your weight (kg): ")
            weight = input()
            height = int(height)
            weight = int(weight)
        else: 
            jarvis.say("Please insert your height (feet): ")
            feet = input()
            jarvis.say("Please insert your height (inches): ")
            inches = input()
            jarvis.say("Please insert your weight (lbs): ")
            weight = input()

            height = int(feet)*12 + int(inches)
            weight = int(weight)
        return height, weight