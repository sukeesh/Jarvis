from plugin import plugin
import random


def spinit(list):
    return(random.choice(list))


@plugin("spinwheel")
def spin(jarvis, s):
    """
    \nThis code picks one of the random inputs given by the user
    smilar to spin wheel

    """
    jarvis.say(' ')
    jarvis.say('welcome to spin the wheel\n')
    jarvis.say('enter the number of elements in the wheel')
    num = jarvis.input_number()
    jarvis.say('enter the elements one after another\n')
    wheel = []
    for i in range(0, int(num)):
        entry = jarvis.input()
        wheel.append(entry)
    reply = 'y'
    while (reply == 'y'):
        jarvis.say('Let the wheel spin !!!!!!!!!\n')
        jarvis.say('result is: ' + spinit(wheel))
        jarvis.say('Do you want to spin again?? press:y ')
        reply = jarvis.input()
    jarvis.say("Thank you for trying spin wheel ")
