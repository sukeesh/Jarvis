from colorama import Fore
from plugin import plugin
import random

"""
simple WORDLE game
"""


def load_dictionary(file_path):
    with open(file_path) as f:
        words = [line.strip() for line in f]
    return words


def is_valid_guess(guess, guesses):
    return len(guess) == 5 and guess in guesses


def evaluate_guess(guess, word):
    str = ""

    for i in range(5):
        if guess[i] == word[i]:
            str += "\033[32m" + guess[i]
        else:
            if guess[i] in word:
                str += "\033[33m" + guess[i]
            else:
                str += "\033[0m" + guess[i]

    return str + "\033[0m"


def wordle(guesses, answers, jarvis):
    jarvis.say("Welcome to WORDLE! You get 6 chances to guess a 5-letter word.")
    jarvis.say("To quit WORDLE type in 'q'")
    secret_word = random.choice(answers).lower()

    attempts = 1
    max_attempts = 6

    while attempts <= max_attempts:

        guess = jarvis.input("Enter Guess #" + str(attempts) + ": ").lower()

        if guess == "q":
            break

        if not is_valid_guess(guess, guesses):
            jarvis.say("Invalid guess. Please enter an English word with 5 letters.", Fore.RED)
            continue

        if guess == secret_word:
            jarvis.say("Congratulations! You guessed the word: " + secret_word, Fore.GREEN)
            break

        attempts += 1
        feedback = evaluate_guess(guess, secret_word)
        jarvis.say(feedback, Fore.GREEN)

    if attempts > max_attempts:
        jarvis.say("Game over. The secret word was: " + secret_word, Fore.RED)


answers_dictionary = 'jarviscli/data/wordle_files/answers.txt'
guesses_dictionary = 'jarviscli/data/wordle_files/guesses.txt'

guesses = load_dictionary(guesses_dictionary)
answers = load_dictionary(answers_dictionary)


@plugin("wordle")
def game(jarvis, s):
    wordle(guesses, answers, jarvis)
