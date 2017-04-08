from colorama import Fore
from aiml.brain import Brain


def main():
    brain = Brain()
    print(Fore.BLUE +
          "Ask me anything\n type 'leave' to stop" + Fore.RESET)
    stay = True

    while stay:
        try:
            text = str.upper(raw_input(Fore.RED + ">> " + Fore.RESET))
        except:
            text = str.upper(input(Fore.RED + ">> " + Fore.RESET))
        if text == "LEAVE":
            print("thanks for talking to me")
            stay = False
        else:
            print(brain.respond(text))
