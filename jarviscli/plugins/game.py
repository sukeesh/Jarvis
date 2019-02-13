from plugin import plugin, alias
from random import randint
from colorama import Fore, Style


# function for generating 4-digit number
def gen_num():
    a = randint(1, 9)
    b = randint(0, 9)
    c = randint(0, 9)
    d = randint(0, 9)
    while b == a:
        b = randint(0, 9)
    while c == b or c == a:
        c = randint(0, 9)
    while d == a or d == b or d == c:
        d = randint(0, 9)
    return a, b, c, d


# function for checking if there is any match
def check(checker, guess_num, div, md, true_rank, cows, bulls):
    r = int(guess_num % md / div)
    if checker[r] > 0:
        if checker[r] == true_rank:
            bulls += 1
        else:
            cows += 1
    return cows, bulls


@alias("bulls")
@plugin("game")
def bulls_and_cows(jarvis, s):
    """"""
    jarvis.say('')
    jarvis.say(Fore.GREEN + 'Welcome to text game Bulls and Cows!\n')
    jarvis.say(Fore.CYAN + 'Rules of the game:\n')
    jarvis.say('* You should guess 4-digit number where all digits are different.')
    jarvis.say('* After each try you will receive the number of matches.')
    jarvis.say(
        '* If the matching digits are in their right positions, they are "bulls"')
    jarvis.say('* Otherwise, if in different positions, they are "cows".')
    jarvis.say(Fore.CYAN + 'Example:')
    jarvis.say(
        '\tSecret number: 4271\n\tYour try: 1234\n\tAnswer: 1 bull and 2 cows.')
    jarvis.say('\tThe bull is "2", the cows are "4" and "1".')
    jarvis.say(Fore.CYAN + 'Lets start? Type "g" to start or "q" to quit:')

    while(True):
        st = jarvis.input()
        if st == 'q':
            jarvis.say(
                Fore.CYAN
                + 'Thank you for playing! New games are coming soon!')
            break
        else:
            tries = int(0)
            a, b, c, d = gen_num()

            # set 'checker' with 10 entries for digits 0-9
            checker = [0] * 10
            checker[a] = int(1)
            checker[b] = int(2)
            checker[c] = int(3)
            checker[d] = int(4)
            jarvis.say(Fore.CYAN + 'Secret number was generated!')

            # loop while the secret number is found or user quits
            while(True):
                jarvis.say(
                    Fore.CYAN
                    + 'Enter your guess, please (type "q" to quit):')
                guess_num = jarvis.input()
                if guess_num == 'q':
                    jarvis.say(Fore.CYAN + 'Thank you for playing!')
                    return
                tries += 1
                guess_num = int(guess_num)
                cows = int(0)
                bulls = int(0)
                cows, bulls = check(
                    checker, guess_num, 1000, 10000, checker[a], cows, bulls)
                cows, bulls = check(
                    checker, guess_num, 100, 1000, checker[b], cows, bulls)
                cows, bulls = check(
                    checker, guess_num, 10, 100, checker[c], cows, bulls)
                cows, bulls = check(
                    checker, guess_num, 1, 10, checker[d], cows, bulls)
                jarvis.say(
                    Fore.CYAN
                    + 'Cows: '
                    + str(cows)
                    + '\tBulls: '
                    + str(bulls)
                    + '\n')
                if bulls == 4:
                    jarvis.say(Fore.CYAN
                               + 'Congratulations! Your guess is right:')
                    jarvis.say(
                        '\t'
                        + Fore.GREEN
                        + str(a)
                        + str(b)
                        + str(c)
                        + str(d))
                    jarvis.say(
                        Fore.CYAN
                        + 'You made '
                        + Fore.GREEN
                        + str(tries)
                        + Fore.CYAN
                        + ' tries.')
                    jarvis.say(Fore.CYAN
                               + 'Start a new game or quit? (Type "s" or "q"):')
                    break
