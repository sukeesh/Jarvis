import random
from plugin import plugin, alias

ball_top = """       _.a$$$$$a._
      ,$$$$$$$$$$$$$.
    ,$$$$$$$$$$$$$$$$$.
   d$$$$$$$$$$$$$$$$$$$b
  d$$$$$$$$~`__~$$$$$$$$b
 ($$$$$$$p   _   q$$$$$$$)'"""

ball_bot = """($$$$$$$b       d$$$$$$$)
  q$$$$$$$$a._.a$$$$$$$$p
   q$$$$$$$$$$$$$$$$$$$p
    `$$$$$$$$$$$$$$$$$'
      `$$$$$$$$$$$$$'
        `~$$$$$$$~"""

# List of responses for the Magic 8 Ball
responseList = ["It is certain.", "It is decidedly so.", "Do it.", "Yes, definitely.",
                "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook: good.", "Yes.", "Signs point to yes.",
                "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
                "The dark side clouds everything. Impossible to see, the future is", "Concentrate, and ask again.",
                "Don't count on it.", "My reply is no.", "My sources say no.",
                "Outlook: not so good.", "Very doubtful."]

# List of responses when the user does not enter a question/query.
emptyList = ["You didn't ask anything, try again.", "Hey, your keyboard has other buttons, just FYI if you didn't know.",
             "Try again", "Hey, you're paying; not me. I don't have to ask anything, so try again.",
             "I hope you don't think this is a date. Try again", "Uhh, why did you even come here? Try again."]

# List of responses when exiting the program
exitList = ["Return should you wish to make a decision or require an answer to a burning inquiry.",
            "May the gods shine upon you.", "May the divines be with you.", "Wait, you forgot to pay!",
            "Will that be cash, Venmo, Zelle, or CashApp? Yes, I do take BitCoin and Ethereum.", "Always at your service."]


class BColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


@alias("magic 8 ball")
@plugin("magic8ball")
class Magic8Ball:

    def __call__(self, jarvis, s):
        self.jarvis = jarvis
        self.s = s
        self.magic8ball_question(jarvis, s)
        
    def magic8ball_question(self, s, jarvis):
        print(f"{BColors.GREEN} +=== What is thy inquiry, great end-user? Or enter 'quit' "
              f"if you wish to remain blind to the truth. ===+\n{BColors.ENDC}")
        question = input("=> ")

        self.magic8ball_response(question)

    def magic8ball_response(self, question):
        # Checks if user inputs 'quit' as an answer to continue using the program to ask another question.
        if question.casefold() == "quit":
            print("\n", "+=== ", random.choice(exitList), " ===+")

        # Checks for blank user inputs and responds to try again
        elif question == "":
            print("\n", BColors.FAIL, "+=== ", random.choice(emptyList), " ===+", "\n", BColors.ENDC)

            print(f"{BColors.GREEN} +=== What is thy inquiry, great end-user? "
                  f"Or enter 'quit' if you wish to remain blind to the truth. ===+\n{BColors.ENDC}")
            question = input("=> ")

            self.magic8ball_response(question)

        # Displays response from list and asks user if they want to ask more questions, otherwise ends
        else:
            response = random.choice(responseList)

            print(BColors.BLUE, "\n", ball_top, BColors.ENDC)
            print(BColors.GREEN, response.center(26, " "), BColors.ENDC)
            print(BColors.BLUE, ball_bot, BColors.ENDC, "\n")

            print(BColors.GREEN, " +=== Do you have any further inquiries you wish to input? ===+\n", BColors.ENDC)
            question_2 = input("=> ")

            if question_2.casefold() == "yes":
                return self.magic8ball_question(self.s, self.jarvis)
            else:
                print(BColors.GREEN, "\n", "+=== ", random.choice(exitList), " ===+", BColors.ENDC)
