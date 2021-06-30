from plugin import plugin

from math import sqrt


@plugin("prime")
def prime(jarvis, s):
    """
    Check if the number is prime or not
    """

    if s == "":
        s = jarvis.input("What's your number ? ")
    try:
        n = int(s)
    except ValueError:
        jarvis.say("That's not a number !")
        return
    else:
        if n < 0:
            jarvis.say("That's not a natural number")
        else:
            if n % 2 == 0:
                jarvis.say("That's not a prime number")
                return
            for i in range(3, int(sqrt(n)) + 1, 2):
                if n % i == 0:
                    jarvis.say("That's not a prime number")
                    return
            jarvis.say("Congrats ! It's a prime number !")
