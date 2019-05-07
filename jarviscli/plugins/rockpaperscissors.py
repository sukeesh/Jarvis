from plugin import plugin
import random

@plugin('rockpaperscissors')
class rockpaperscissors():

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

        while( i <= int(rounds)):

            user_move = self.get_users("Enter your move: ")

            if (user_move == 'exit'):
                i = i + 1
                exit = True
                break

            if (user_move == "score"):
                txt = "You:" + str(user_score) + "  Jarvis:" + str(jarvis_score) + "  "
                if (user_score > jarvis_score):
                    txt = txt + "You Winning"
                elif(user_score < jarvis_score):
                    txt = txt + "You Losing"
                else:
                    txt = txt + "Tie"

                jarvis.say(txt)

            if (user_move == "rounds"):
                jarvis.say("The current rounds is " + i + "/" + rounds)

            jarvis_move = self.get_jarvis()
            jarvis.say("Jarvis move: " + jarvis_move)

            g = self.game(user_move, jarvis_move)

            if (g == "W"):
                user_score = user_score + 1
                jarvis.say("\t" + "You WIN")
            elif (g == "L"):
                jarvis_score = jarvis_score + 1
                jarvis.say("\t" + "Jarvis WIN")
            else:
                jarvis.say("\t" + "TIE")

            i = i + 1

        jarvis.say("")
        jarvis.say("\t" + "THE GAME END")
        jarvis.say("\t" + "--SCORE--")
        jarvis.say("\t" + "YOU: " + str(user_score) + "\t" + "JARVIS: " + str(jarvis_score))

        if (user_score > jarvis_score):
            txt = "\tYOU WIN!!"
        elif (user_score < jarvis_score):
            txt = "\tYOU LOSE!"
        else:
            txt = "\tTIE"

        if (exit == True):
            jarvis.say("You terminate the game at i round")

        jarvis.say(txt)
        jarvis.say("GAME OVER")


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

        return moves[random.randint(0,2)]

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
