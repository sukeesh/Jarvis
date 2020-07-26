from plugin import plugin
import os
from colorama import Fore


FILE_PATH = os.path.abspath(os.path.dirname(__file__))
NUM_NEXT = 100


@plugin("pi")
def next_pi(jarvis, s):
    jarvis.say("Pi equals 3.14...", Fore.GREEN)
    # today = datetime.date.today()

    # print(today)

    pi_file = open(os.path.join(FILE_PATH, '../data/pi.txt'), 'r')
    pi_number = pi_file.read()
    index = 4
    while True:
        user_input = jarvis.input("Enter \'n\' to print next {} digits : ".format(str(NUM_NEXT)))
        if (user_input != 'n'):
            break
        jarvis.say(pi_number[index: index + NUM_NEXT], Fore.GREEN)
        index += NUM_NEXT
