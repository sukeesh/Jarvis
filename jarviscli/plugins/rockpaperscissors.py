from plugin import plugin
from colorama import Back, Fore, Style
import random


@plugin('rockpaperscissors')
class rockpaperscissors():
    """
    rockpaperscissors Dcoumentation.
    rockpaperscssors is the game Rock - Paper - Scissors that we all know with Jarvis as opponent.

    First of all you enter how many rounds you will play (max. 100).
    And then the game starts.
    In every round you will request to enter your move.

    'r' for rock.
    'p' for paper.
    's' for scissors.

    Also you can exit the game whenever you like by entering as move 'exit' and also you can display the score whenever
    you want by entering 'score'.

    You can display the current round by entering 'rounds'.

    """

    def __call__(self, jarvis, s):
        jarvis.say("!! Welcome to Rock Paper Scissors !!")
        jarvis.say("!A game to play with Jarvis as rival!")

        rounds = self.get_rounds("Enter how many rounds you will play (max. 100): ")

        jarvis.say("OK")
        jarvis.say("The game begins")

        user_score = 0
        jarvis_score = 0

        exit = False

        i = 1

        while(i <= int(rounds)):

            user_move = self.get_users("Enter your move: ")

            if (user_move == 'exit'):
                exit = True
                break

            if (user_move == "score"):
                txt = "You:" + str(user_score) + "  Jarvis:" + str(jarvis_score) + "  "
                if (user_score > jarvis_score):
                    txt = txt + Back.GREEN + "You Winning" + Back.RESET
                elif(user_score < jarvis_score):
                    txt = txt + Back.RED + "You Losing" + Back.RESET
                else:
                    txt = txt + Back.WHITE + "Tie" + Back.RESET

                jarvis.say(txt)
                continue

            if (user_move == "rounds"):
                jarvis.say("The current rounds is " + str(i) + "/" + str(rounds))
                continue

            jarvis_move = self.get_jarvis()
            jarvis.say("Jarvis move: " + jarvis_move)

            g = self.game(user_move, jarvis_move)

            if (g == "W"):
                user_score = user_score + 1
                jarvis.say("\t" + Back.GREEN + "You WIN" + Back.RESET)
                i = i + 1
            elif (g == "L"):
                jarvis_score = jarvis_score + 1
                jarvis.say("\t" + Back.RED + "Jarvis WIN" + Back.RESET)
                i = i + 1
            else:
                jarvis.say("\t" + Back.MAGENTA + "TIE" + Back.RESET)
                i = i + 1

        jarvis.say("")
        jarvis.say("\t\t" + "GAME OVER")
        jarvis.say("\t\t" + "--SCORE--")
        jarvis.say("\t" + "YOU: " + str(user_score) + "\t" + "JARVIS: " + str(jarvis_score))

        if (user_score > jarvis_score):
            txt = Back.GREEN + "\t\tYOU WIN!!" + Back.RESET
        elif (user_score < jarvis_score):
            txt = Back.RED + "\t\tYOU LOSE!" + Back.RESET
        else:
            txt = Back.WHITE + "\t\tTIE" + Back.RESET

        if (exit is True):
            r = str(i - 1)

            if (r == "1"):
                r = r + "st"
            elif (r == "2"):
                r = r + "nd"
            elif (r == "3"):
                r = r + "rd"
            else:
                r = r + "th"
            jarvis.say("You terminate the game at " + r + " round")

        jarvis.say(txt)

    def get_rounds(self, prompt):

        while True:
            rounds = input(prompt)
            if (int(rounds) <= 100):
                return rounds
            else:
                prompt = 'Laps should be under 100 \n'

    def get_users(self, prompt):

        moves = ["rock", "r", "paper", "p", "scissors", "s", "exit", "score", "rounds"]

        while True:
            u = input(prompt).lower()
            if u in moves:
                if (u == "rock"):
                    u = "r"
                elif (u == "paper"):
                    u = "p"
                elif (u == "scissors"):
                    u = "s"
                else:
                    return u

                return u
            else:
                prompt = 'Please enter a valid move: '
                continue

    def get_jarvis(self):

        moves = ["r", "p", "s"]

        return moves[random.randint(0, 2)]

    def game(self, umove, jmove):

        condition = ""

        if (umove == jmove):
            condition = "T"

        else:
            if ((umove == "r" and jmove == "s") or (umove == "s" and jmove == "p") or (umove == "p" and jmove == "r")):
                condition = "W"
            else:
                condition = "L"

        return condition
