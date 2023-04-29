from random import choice
import os
from plugin import plugin


@plugin("wordle")
class Wordle():
    def __call__(self, jarvis, s):
        logo = '''
 .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
| | _____  _____ | || |     ____     | || |  _______     | || |  ________    | || |   _____      | || |  _________   | |
| ||_   _||_   _|| || |   .'    `.   | || | |_   __ \    | || | |_   ___ `.  | || |  |_   _|     | || | |_   ___  |  | |
| |  | | /\ | |  | || |  /  .--.  \  | || |   | |__) |   | || |   | |   `. \ | || |    | |       | || |   | |_  \_|  | |
| |  | |/  \| |  | || |  | |    | |  | || |   |  __ /    | || |   | |    | | | || |    | |   _   | || |   |  _|  _   | |
| |  |   /\   |  | || |  \  `--'  /  | || |  _| |  \ \_  | || |  _| |___.' / | || |   _| |__/ |  | || |  _| |___/ |  | |
| |  |__/  \__|  | || |   `.____.'   | || | |____| |___| | || | |________.'  | || |  |________|  | || | |_________|  | |
| |              | || |              | || |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------' '''
        data_path = os.path.abspath(os.path.dirname(__file__))
        data = data_path[:-8] + '/data/wordle.txt'
        f = open(data, 'r')
        lists_of_words = list(map(lambda x: x.split()[3], f.readlines()))
        wordToGuess = choice(lists_of_words)
        jarvis.say(logo)
        jarvis.say(
            "Welcome to wordle! You get 5 chances to guess the 5 letter word...")
        jarvis.say("After each guess it shows you the result of your answer.")
        jarvis.say(
            "\tG - right position and right letter.\n\tY - right letter wrong position.\n\tW - wrong letter.")

        jarvis.say("\nLet's start the game!")

        lives = 5
        while (lives != 0):
            answerByTheUser = jarvis.input("Enter the guess: ")
            lives -= 1

            if lives == 0:
                jarvis.say(
                    f"Uh-oh, you are out of lives.\nThe correct word was: \"{wordToGuess}\".")
                jarvis.say("Better luck next time! ")

            elif answerByTheUser.lower() == wordToGuess.lower():
                jarvis.say("Congratulaions! You guessed it right!\n")
                jarvis.say("Lives left: {}".format(lives))
                break

            else:
                for index in range(0, 5):
                    if answerByTheUser[index].lower() == wordToGuess[index].lower():
                        jarvis.say("G ")

                    elif answerByTheUser[index].lower() in list(wordToGuess.lower()):
                        jarvis.say("Y ")

                    else:
                        jarvis.say("W ")
                jarvis.say("Wrong guess...\nTry again: ")
                jarvis.say("Lives left: {}".format(lives))
