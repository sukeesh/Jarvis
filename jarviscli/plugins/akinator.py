from plugin import plugin, require
from colorama import Fore
import akinator
import subprocess
import sys


"""
Simple akinator text based game: think up a character, answer questions and akinator will find it !
https://pypi.org/project/akinator.py/
"""


@require(network=True)
@plugin("akinator")
def akinator_main(jarvis, s):

    opening_message(jarvis)
    jarvis.say('Press "g" to start, or "q" to quit !')
    while True:
        user_in = jarvis.input()
        if user_in == 'q':
            jarvis.say("See you next time :D", Fore.CYAN)
            break
        elif user_in == 'g':
            main_game(jarvis)
            break
        else:
            jarvis.say('Press "g" to start, or "q" to quit !')


# Helper methods


def opening_message(jarvis):
    ''' Messages displayed when akinator called '''

    jarvis.say('')
    jarvis.say('Let\'s play !')
    jarvis.say('You have to think of a public personality, answer to some questions and I will try to guess who it is !')
    jarvis.say('Rules: ')
    print_help(jarvis)


def main_game(jarvis):
    ''' Handling of the akinator library '''

    aki = akinator.Akinator()
    try:
        q = aki.start_game()
    except (akinator.AkiServerDown, akinator.AkiTechnicalError):
        try:
            q = aki.start_game("en2")  # 2nd server if the 1st is down
        except (akinator.AkiServerDown, akinator.AkiTechnicalError):
            q = aki.start_game("en3")  # 3rd server if the 2nd is down

    # questions loop
    while aki.progression <= 80:
        try:
            a = input(q + "\n")
        except EOFError:
            a = "cantDoThat"
        if a == "b":
            try:
                q = aki.back()
            except akinator.CantGoBackAnyFurther:
                pass
        elif a == "h":
            print_help(jarvis)
        elif a == "q":
            jarvis.say("See you next time !")
            return
        else:
            try:
                q = aki.answer(a)
            except akinator.InvalidAnswerError:
                jarvis.say("answer not understood, type \"h\" for help", Fore.MAGENTA)

    aki.win()

    imageViewerFromCommandLine = {'linux': 'xdg-open',
                                  'win32': 'explorer',
                                  'darwin': 'open'}[sys.platform]  # get an image Viewer
    try:
        subprocess.run([imageViewerFromCommandLine, aki.picture])  # display image of answer
    except Exception:
        pass
    correct = jarvis.input(f"It's {aki.first_guess['name']} ({aki.first_guess['description']})! Was I correct?\n\t")
    if correct.lower() == "yes" or correct.lower() == "y":
        jarvis.say("Yay !!! :D", Fore.GREEN)
    else:
        jarvis.say("Oups :(", Fore.GREEN)


def print_help(jarvis):
    ''' Print help '''
    jarvis.say("To answer, you have the following options: ", Fore.GREEN)
    jarvis.say("\t \"yes\" or \"y\" or \"0\" for YES", Fore.GREEN)
    jarvis.say("\t \"no\" or \"n\" or \"1\" for NO", Fore.GREEN)
    jarvis.say("\t \"i\" or \"idk\" or \"i dont know\" or \"2\" for I DON\'T KNOW", Fore.GREEN)
    jarvis.say("\t \"probably\" or \"p\" or \"3\" for PROBABLY", Fore.GREEN)
    jarvis.say("\t \"probably not\" or \"pn\" or \"4\" for PROBABLY NOT", Fore.GREEN)
    jarvis.say("\t \"q\" to QUIT", Fore.GREEN)
