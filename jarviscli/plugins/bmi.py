from plugin import plugin
from six.moves import input

@plugin()
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


