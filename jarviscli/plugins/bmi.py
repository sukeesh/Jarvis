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
            calc = self.calc_bmi_m(jarvis)
        else:
            calc = self.calc_bmi_i(jarvis)

        state = self.find_body_state(jarvis, calc)


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

    def calc_bmi_m(self, jarvis):

        jarvis.say("Please insert your height")
        height = input()
        jarvis.say("Please insert your weight")
        weight = input()

        height = int(height)
        weight = int(weight)

        """Calculate bmi"""
        height = height/100
        bmi = weight/height**2
        return bmi

    def calc_bmi_i(self, jarvis):

        jarvis.say("Please insert your height")
        height = input()
        jarvis.say("Please insert your weight")
        weight = input()

        height = int(height)
        weight = int(weight)

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


'''
def bmi(jarvis, s):
    """
    Calculates Body Mass Index.
    It is available for metric and imperial system
    -- Type bmi, press enter and then follow the instructions
    """

    jarvis.say("Type m for metric and i for imperial system")
    syst = input()
    jarvis.say("Please insert your height")
    height = input()
    jarvis.say("Please insert your weight")
    weight = input()

    height = int(height)
    weight = int(weight)

    """Calculate bmi"""
    if syst == "m":
        height = height/100
        bmi = weight/height**2
    else:
        bmi = weight/height**2 * 703

    """ Find body state """
    if bmi < 18.5:
        state = "Underweight"
    elif bmi < 24.9:
        state = "Healthy"
    elif bmi < 30:
        state = "Overweight"
    else:
        state = "Obese"
    print(str(bmi), " ", state)
'''

