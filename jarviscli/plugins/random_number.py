from plugin import plugin
import random

@plugin("random number")
def random_password(jarvis, s):
    stringFail = True

    while (stringFail):
        try:
            smallest_number = int(input("Enter the smallest number possible: "))
            higher_number = int(input("Enter the higher number possible: "))
            stringFail = False
        except:
            print('Only integers will be accepted')

    """If the user change the order of input"""
    if(higher_number < smallest_number):
        aux = higher_number
        higher_number = smallest_number
        smallest_number = aux

    preText = "Your random number is";
    random_number = random.randint(smallest_number,higher_number+1)
    print(preText, random_number)