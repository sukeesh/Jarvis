from plugin import plugin
from colorama import Fore


@plugin("motivate me")
def motivate(jarvis, s):
    quotes = ["You're gonna wake up and work hard at it", "Don't let you're dreams be dreams",
              "Make your dreams come true", "Nothing is impossible"]
    quotes += ['Yes you can', 'JUST DO IT!', 'Just do it', 'Stop giving up', 'Yesterday you said tommorow',
               'You should get to the point where anyone else quits and you\'re not gonna stop there']
    quotes += ['Make your dreams come true', 'Nothing is impossible',
               'Go what are you waiting for', 'JUST DO IT', 'Make your dreams come true', 'Just do it']

    ind = 0

    jarvis.say("Enter \'n\' to print nextquote : ", Fore.GREEN)

    while True:
        motivational_quote = quotes[ind]
        jarvis.say(motivational_quote, Fore.GREEN)
        user_input = jarvis.input()
        if (user_input != 'n'):
            break
        ind += 1
        if (ind == len(quotes)):
            break

    jarvis.say('That\'s it, go and work now!')
