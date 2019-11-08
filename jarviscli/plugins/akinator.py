from plugin import plugin
from colorama import Fore
from akinator import Akinator

'''
Simple akinator text based game
https://pypi.org/project/akinator.py/
'''
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
                

########################################
######## HELPER METHODS ################
########################################

''' Messages displayed when akinator called ''' 
def opening_message(jarvis):
    jarvis.say('')
    jarvis.say('Let\'s play !')
    jarvis.say('You have to think of a public personality, answer to some questions and I will try to guess who it is !')
    jarvis.say('Rules: ', Fore.CYAN)
    jarvis.say('\t Answer akinator\'s questions with yes (y), no (n),  don\'t know (idk), probably (p) or probably not (pn)')


def main_game(jarvis):
    aki = Akinator() 
    try:
       q = aki.start_game() 
    except (akinator.AkiServerDown, akinator.AkiTechnicalError):
        try: 
            q = aki.start_game("en2")
        except (akinator.AkiServerDown, akinator.AkiTechnicalError):
            q = aki.start_game("en3")

    # questions loop
    while aki.progression <= 80: 
        a = input(q + "\n\t")
        if a == "b":
            try:
                q = aki.back()
            except akinator.CantGoBackAnyFurther: 
                pass
        else: 
            try:
                q = aki.answer(a)
            except akinator.InvalidAnswerError: 
                jarvis.say("answer not understood, type \"h\" for help")
                # TODO: actually put help 

    aki.win()

    correct = jarvis.input(f"It's {aki.name} ({aki.description})! Was I correct?\n{aki.picture}\n\t")
    if correct.lower() == "yes" or correct.lower() == "y":
        jarvis.say("Yay !!! :D")
    else:
        jarvis.say("Oups :(")
