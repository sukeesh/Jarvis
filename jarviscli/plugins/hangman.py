from plugin import plugin
from random_word import RandomWords

def continueOrNot():
    terminationFlag = 0
    desire = input("Do You Want To Play Again? (Y/N) ")
    desire = desire.strip()
    desire = desire.lower()
    while desire != "n" and desire != "y":
        desire = input("Enter proper answer! (Y/N) ")
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
        if phase == 1:
            stickman = stickman + "   |---"
            stickman = stickman + "   |   '"
            stickman = stickman + "   |   O"
        elif phase == 2:
            stickman = stickman + "   | --|--"
        elif phase == 3:
            stickman = stickman + "   |'  |  '"
        elif phase == 4:
            stickman = stickman + "   |   |  "
        elif phase == 5:
            stickman = stickman + "   |  ---"
        elif phase == 6:
            stickman = stickman + "   | |   |"
        elif phase == 7:
            stickman = stickman + "   | |   |"
        elif phase == 8:
            stickman = stickman + "   |__   __"
        phase = phase + 1
    print(stickman)

@plugin('hangman')
def hangman(jarvis, s):
    print("Hello Hangman Game Is About To Begin!\n")
    print("Guess Should Be Characters!\n")
    randomWords = RandomWords()
    terminateFlag = 0

    while not terminateFlag:
        lives = 8
        usedLetters = ""
        actualWordToGuess = ""
        while len(actualWordToGuess) < 4:
            try :
                actualWordToGuess = randomWords.get_random_word()
            except:
                continue
        actualWordToGuess = actualWordToGuess.lower()
        wordToGuess = ""
        for x in range(len(actualWordToGuess)):
            wordToGuess = wordToGuess+"_"
        while 1:
            if lives == 8:
                print("You Lost!")
                break
            if actualWordToGuess == wordToGuess:
                print("You Won!")
                break
            print("Word To Guess Looks Like This : "+wordToGuess)
            guess = input("Enter Your Guess : ")
            guess = guess.strip()
            guess = guess.lower()
            if guess == "stop":
                print("You Stopped Playing Hangman!")
                break
            if len(guess) == 0:
                print("Woops! You Have Not Entered Anything")
                lives = lives - 1
                print("Penalty! Lives Decrease By 1, Remains : "+str(lives))
                drawStickMan(8-lives)
                continue
            if len(guess) > 1:
                print("Woops! You Have Entered Input Longer Than Character Size")
                lives = lives - 1
                print("Penalty! Lives Decrease By 1, Remains : "+str(lives))
                drawStickMan(8-lives)
                continue
            if guess in usedLetters:
                print("Woops! You Have Entered Letter That Is Already Used")
                lives = lives - 1
                print("Penalty! Lives Decrease By 1, Remains : "+str(lives))
                drawStickMan(8-lives)
                continue
            if guess not in actualWordToGuess:
                print("Woops! You Have Entered Wrong Guess\n")
                lives = lives - 1
                print("Penalty! Lives Decrease By 1, Remains : "+str(lives))
                drawStickMan(8-lives)
                continue
            if guess.lower() in actualWordToGuess:
                print("YES! You Have Entered Correct Guess")
                drawStickMan(8-lives)

            usedLetters = usedLetters + guess
            newWordToGuess = ""
            for position in range(len(actualWordToGuess)):
                if actualWordToGuess[position] == guess:
                    newWordToGuess = newWordToGuess + guess
                else:
                    newWordToGuess = newWordToGuess + wordToGuess[position]
            wordToGuess = newWordToGuess

        print("Word To Guess Was : "+actualWordToGuess.upper())
        terminateFlag = continueOrNot()