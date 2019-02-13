from plugin import plugin
import random
import string


@plugin("random password")
def random_password(jarvis, s):
    stringFail = True

    while(stringFail):
        try:
            stringLength = int(jarvis.input("Enter password length: "))
            stringFail = False
        except BaseException:
            print('Only integers will be accepted')

    prompt = 'Do you want special characters?(y/n): '

    """Checks if the input the user gave is valid(either y or n)"""
    while True:
        try:
            user_input = jarvis.input(prompt)
        except ValueError:
            jarvis.say("\nSorry, I didn't understand that.")
            continue

        if (user_input != 'y') and (user_input != 'n'):
            jarvis.say("\nSorry, your response is not valid.")
            continue
        else:
            break

    if user_input == 'n':
        password = string.ascii_letters + string.digits
    else:
        password = string.ascii_letters + string.digits + string.punctuation

    """Generate a random string of fixed length """
    preText = 'Your random password is: '
    print(preText + ''.join(random.choice(password)
                            for _ in range(stringLength)))
