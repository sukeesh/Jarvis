from plugin import plugin
import time
import random


@plugin('memory')
class Memory:
    """
    Welcome to the Short-Term Memory Trainer! Here you can find 
    all the functionalities of this plugin.
    Usage: Type memory, press enter and follow the instructions
    Functionalities: You can train your memory by recalling a 
    random generated number.
    Find out how many digits you can remember.
    """

    def __call__(self, jarvis, s):
        jarvis.say("Welcome to Memory Trainer.")
        jarvis.say("We will train you by giving a number to remember.")
        jarvis.say("The number won't be visible for very long.")
        jarvis.say("Each time the number will get 1 more digit.")
        answer = self.get_answer(jarvis)
        if answer == 1:
            self.trainer(jarvis)
        else:
            return

    def get_answer(self, jarvis):
        """
        Asks the user you check if he is ready to start the game
        1 for ready, 2 for not ready
        """
        jarvis.say("Are you ready to play?")
        while True:
            try:
                jarvis.say("Press 1 for Yes. \nPress 2 for No.")
                c = int(input("Your choice: "))
                if c != 1 or c != 2:
                    raise ValueError('Please give a valid input')
                break
            except ValueError:
                print("Please give a valid input")
        return c

    def trainer(self, jarvis):
        """
        User guesses the number, checks if the guess is correct.
        First wrong guess means the user has lost.
        """
        lost = False
        number = ""
        while not lost:
            number = self.create_number(jarvis, number)
            print("The number will only be visible for a few seconds.")
            print(number, end="\r")
            time.sleep(2 * len(number))
            jarvis.say("Time ended.")
            guess = str(input("Type your guess:"))
            if guess == number:
                jarvis.say("Correct guess of "+ str(len(number))+ " digits")
            else:
                jarvis.say("Wrong guess.")
                jarvis.say("You were able to remember "+ str(len(number) - 1)+ " digits")
                jarvis.say("Be sure to train again.")
                lost = True
        return

    def create_number(self, jarvis, number):
        """
        Creates the new number with the new digit

        """
        digit = str(random.randint(0, 9))
        new = number + digit
        return new
