from plugin import plugin
import random
import string


@plugin("random_password")
def random_password(jarvis, s):

    stringLength = 10
    """Generate a random string of fixed length """
    lettersAndDigits = string.ascii_letters + string.digits
    preText = 'Your random password is: '
    print(preText + ''.join(random.choice(lettersAndDigits) for i in range(stringLength)))
