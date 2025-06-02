import math
from plugin import plugin
# A simple plugin to print all prime factors of a given number n

@plugin("factor")
def factor(jarvis, s):
    try:
        n = int(input("Enter a number for me to factorize: "))

        factors = []
        while n % 2 == 0:
            factors.append(2)
            n = n // 2

        for i in range(3, int(math.sqrt(n)) + 1, 2):
            while n % i == 0:
                factors.append(i)
                n = n // i

        if n > 2:
            factors.append(n)  # if n is prime

        result = ' x '.join(map(str, factors))
        jarvis.say(result)
    except ValueError:
        jarvis.say("Invalid input. Please enter a positive integer.")
