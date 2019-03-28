from plugin import plugin
import random
import string


@plugin("random password")
def random_password(jarvis, s):
    stringFail = True

    while(stringFail):
        try:
            stringLength = int(input("Enter password length: "))
            stringFail = False
        except:
            print('Only integers will be accepted')

    """Generate a random string of fixed length """
    lettersAndDigits = string.ascii_letters + string.digits
    preText = 'Your random password is: '
    print(preText + ''.join(random.choice(lettersAndDigits) for i in range(stringLength)))
