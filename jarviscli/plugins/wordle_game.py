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
        data = data_path + '/words_folder/words'
        lists_of_words = list(map(lambda x : x.split()[3],f.readlines()))
        wordToGuess = choice(lists_of_words)
        if '\n' in wordToGuess:
            wordToGuess[-1] = ''

        jarvis.say(logo)

        jarvis.say("Welcome to wordle! You get 5 chances to guess the 5 letter word...")
        jarvis.say("After each guess it shows you the result of your answer.")
        jarvis.say("\tG - right position and right letter.\n\tY - right letter wrong position.\n\tW - wrong letter.")

        jarvis.say("\nLet's start the game!")

        lives = 5
        while(lives != 0):
            answerByTheUser = jarvis.input("Enter the guess: ")
            lives -= lives

            if lives == 0:
                jarvis.say(f"Uh-oh, you are out of lives.\nThe correct word was: \"{wordToGuess}\".")
                jarvis.say("Better luck next time! ")


            elif answerByTheUser == wordToGuess:
                jarvis.say("Congratulaions! You guessed it right!\n")
                jarvis.say("Lives left: ", lives)
                break

            else:
                for index in range(0,5):
                    if answerByTheUser[index] == wordToGuess[index]:
                        jarvis.say("G ", Fore = 'green')

                    elif answerByTheUser[index] in list(wordToGuess):
                        jarvis.say("Y ", Fore = 'yellow')

                    else:
                        jarvis.say("W ", Fore = 'red')
                jarvis.say("Wrong guess...\nTry again: ")
                jarvis.say("Lives left: ", lives)

