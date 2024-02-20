import sympy
from colorama import Fore
from jarviscli import entrypoint
from jarviscli.plugins.eval import calc


@entrypoint
def factor(jarvis, s):
    """
    Jarvis will factories
    -- Example:
        factor x**2-y**2
    """
    tempt = s.replace(" ", "")
    if len(tempt) > 1:
        calc(jarvis, tempt, formatter=sympy.factor)
    else:
        jarvis.say("Error: Not in correct format", Fore.RED)
