from plugin import plugin
import random
import string
from colorama import Fore


@plugin("random password")
def random_password(jarvis, s):
    while True:
        try:
            string_length = int(jarvis.input("Enter password length: "))
            break
        except ValueError:
            jarvis.say('Only integers will be accepted', Fore.RED)

    prompt = 'Do you want special characters?(y/n): '
    password = string.ascii_letters + string.digits

    """Checks if the input the user gave is valid(either y or n)"""
    while True:
        try:
            user_input = jarvis.input(prompt)
        except ValueError:
            jarvis.say("Sorry, I didn't understand that.", Fore.RED)
            continue

        if user_input == 'y':
            password += string.punctuation
        elif user_input != 'n':
            jarvis.say("Sorry, your response is not valid.", Fore.RED)
            continue
        break

    """Generate a random string of fixed length """
    pre_text = 'Your random password is: '
    jarvis.say(pre_text + ''.join(random.choice(password)
                                  for _ in range(string_length)))
