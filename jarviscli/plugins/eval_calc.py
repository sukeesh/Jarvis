# -*- coding: utf-8 -*-
from colorama import Fore
from jarviscli import entrypoint
from jarviscli.plugins.eval import calc


@entrypoint
def calculate(jarvis, s):
    """
    Jarvis will get your calculations done!
    -- Example:
        calculate 3 + 5
    """
    tempt = s.replace(" ", "")
    if len(tempt) > 1:
        calc(jarvis, tempt, formatter=lambda x: x)
    else:
        jarvis.say("Error: Not in correct format", Fore.RED)
