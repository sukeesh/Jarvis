from plugin import plugin
from random_word import RandomWords as random_words


@plugin('hangman')
def hangman(jarvis, s):
    initial_text = "#########################################\n" \
                   "# Hello Hangman Game Is About To Begin! #\n" \
                   "#     Guesses Should Be Characters!     #\n" \
                   "#        Type 'stop' To End Game!       #\n" \
                   "#########################################\n"
    print(initial_text)
    random_words = random_words()
    terminate_flag = 0

    while not terminate_flag:
        lives = 8
        used_letters = ""
        actual_word_to_guess = ""
        while len(actual_word_to_guess) < 4:
            try:
                actual_word_to_guess = random_words.get_random_word()
            except BaseException:
                continue
        actual_word_to_guess = actual_word_to_guess.lower()
        word_to_guess = ""
        for x in range(len(actual_word_to_guess)):
            word_to_guess = word_to_guess + "_"
        while True:
            if lives == 0:
                print("You Lost!\n")
                break
            if actual_word_to_guess == word_to_guess:
                print("You Won!\n")
                break
            print("Word To Guess Looks Like This : " + word_to_guess + "\n")
            guess = input("Enter Your Guess : ")
            print("\n")
            guess = guess.strip()
            guess = guess.lower()
            if guess == "stop":
                print("You Stopped Playing Hangman!\n")
                break
            if len(guess) == 0:
                print("Woops! You Have Not Entered Anything\n")
                lives = lives - 1
                print("Penalty! Lives Decrease By 1, Remains : " + str(lives) + "\n")
                draw_stick_man(8 - lives)
                continue
            if len(guess) > 1:
                print("Woops! You Have Entered Input Longer Than CharacterSize\n")
                lives = lives - 1
                print("Penalty! Lives Decrease By 1, Remains : " + str(lives) + "\n")
                draw_stick_man(8 - lives)
                continue
            if guess in usedLetters:
                print("Woops! You Have Entered Letter That Is Already Used\n")
                lives = lives - 1
                print("Penalty! Lives Decrease By 1, Remains : " + str(lives) + "\n")
                draw_stick_man(8 - lives)
                continue
            if guess not in actual_word_to_guess:
                print("Woops! You Have Entered Wrong Guess\n")
                lives = lives - 1
                print("Penalty! Lives Decrease By 1, Remains : " + str(lives) + "\n")
                draw_stick_man(8 - lives)
                continue
            if guess.lower() in actualWordToGuess:
                print("YES! You Have Entered Correct Guess\n")
                draw_stick_man(8 - lives)

            used_letters = used_letters + guess
            new_word_to_guess = ""
            for position in range(len(actual_word_to_guess)):
                if actual_word_to_guess[position] == guess:
                    new_word_to_guess = new_word_to_guess + guess
                else:
                    new_word_to_guess = new_word_to_guess + word_to_guess[position]
            word_to_guess = new_word_to_guess

        print("Word To Guess Was : " + actual_word_to_guess.upper())
        terminate_flag = continue_or_not()

    good_bye_text = "#########################################\n" \
                    "#               Farewell!               #\n" \
                    "#       May The Force Be With You!      #\n" \
                    "#########################################\n"
    print(good_bye_text)


def continue_or_not():
    termination_flag = 0
    desire = input("Do You Want To Play Again? (Y/N) ")
    print("\n")
    desire = desire.strip()
    desire = desire.lower()
    while desire != "n" and desire != "y":
        desire = input("Enter proper answer! (Y/N) ")
        print("\n")
        desire = desire.strip()
        desire = desire.lower()
    if desire == "n":
        termination_flag = 1
    elif desire == "y":
        print("Hangman Game Resets!\n")
    return termination_flag


def draw_stick_man(phase_main):
    stickman = ""
    phase = 0
    while phase != phase_main:
        if phase == 0:
            stickman = stickman + "   |---\n"
            stickman = stickman + "   |   '\n"
            stickman = stickman + "   |   O\n"
        elif phase == 1:
            stickman = stickman + "   | --|--\n"
        elif phase == 2:
            stickman = stickman + "   |'  |  '\n"
        elif phase == 3:
            stickman = stickman + "   |   |  \n"
        elif phase == 4:
            stickman = stickman + "   |  ---\n"
        elif phase == 5:
            stickman = stickman + "   | |   |\n"
        elif phase == 6:
            stickman = stickman + "   | |   |\n"
        elif phase == 7:
            stickman = stickman + "   |__   __\n"
        phase = phase + 1
    print(stickman)
