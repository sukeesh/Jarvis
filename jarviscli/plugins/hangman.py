from plugin import plugin
from random_word import RandomWords


@plugin('hangman')
def hangman(jarvis, s):
    initialText = "#########################################\n" \
                  "# Hello Hangman Game Is About To Begin! #\n" \
                  "#     Guesses Should Be Characters!     #\n" \
                  "#        Type 'stop' To End Game!       #\n" \
                  "#########################################\n"
    print(initialText)
    randomWords = RandomWords()
    terminateFlag = 0

    while not terminateFlag:
        lives = 8
        usedLetters = ""
        actualWordToGuess = ""
        while len(actualWordToGuess) < 4:
            try:
                actualWordToGuess = randomWords.get_random_word()
            except BaseException:
                continue
        actualWordToGuess = actualWordToGuess.lower()
        wordToGuess = ""
        for x in range(len(actualWordToGuess)):
            wordToGuess = wordToGuess + "_"
        while True:
            if lives == 0:
                print("You Lost!\n")
                break
            if actualWordToGuess == wordToGuess:
                print("You Won!\n")
                break
            print("Word To Guess Looks Like This : " + wordToGuess + "\n")
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
                drawStickMan(8 - lives)
                continue
            if len(guess) > 1:
                print("Woops! You Have Entered Input Longer Than Character Size\n")
                lives = lives - 1
                print("Penalty! Lives Decrease By 1, Remains : " + str(lives) + "\n")
                drawStickMan(8 - lives)
                continue
            if guess in usedLetters:
                print("Woops! You Have Entered Letter That Is Already Used\n")
                lives = lives - 1
                print("Penalty! Lives Decrease By 1, Remains : " + str(lives) + "\n")
                drawStickMan(8 - lives)
                continue
            if guess not in actualWordToGuess:
                print("Woops! You Have Entered Wrong Guess\n")
                lives = lives - 1
                print("Penalty! Lives Decrease By 1, Remains : " + str(lives) + "\n")
                drawStickMan(8 - lives)
                continue
            if guess.lower() in actualWordToGuess:
                print("YES! You Have Entered Correct Guess\n")
                drawStickMan(8 - lives)

            usedLetters = usedLetters + guess
            newWordToGuess = ""
            for position in range(len(actualWordToGuess)):
                if actualWordToGuess[position] == guess:
                    newWordToGuess = newWordToGuess + guess
                else:
                    newWordToGuess = newWordToGuess + wordToGuess[position]
            wordToGuess = newWordToGuess

        print("Word To Guess Was : " + actualWordToGuess.upper())
        terminateFlag = continueOrNot()

    goodByeText = "#########################################\n" \
                  "#               Farewell!               #\n" \
                  "#       May The Force Be With You!      #\n" \
                  "#########################################\n"
    print(goodByeText)


def continueOrNot():
    terminationFlag = 0
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
        terminationFlag = 1
    elif desire == "y":
        print("Hangman Game Resets!\n")
    return terminationFlag


def drawStickMan(phaseMain):
    stickman = ""
    phase = 0
    while phase != phaseMain:
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
