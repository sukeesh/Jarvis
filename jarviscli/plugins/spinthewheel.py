from plugin import plugin
import random
'''This code picks one of the random inputs given by the user
like spin wheel'''


@plugin("spin wheel")
def spin(jarvis, s):
    jarvis.say(' ')
    jarvis.say('welcome to spin the wheel\n')
    jarvis.say('enter the number of elements in the wheel')
    num = jarvis.input()
    intnum = int(num)
    jarvis.say('enter the elements one after another\n')
    wheel = []
    for i in range(0, intnum):
        entry = jarvis.input()
        wheel.append(entry)
    jarvis.say('Let the wheel spin !!!!!!!!!\n')
    jarvis.say('result is: ' + random.choice(wheel))
