import pyautogui
# some_file.py
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, 'jarviscli')

import CmdInterpreter
import requests
from colorama import Fore
from plugin import plugin, require 
import os

@require(network=True)
@plugin("screenshot")
def ss(jarvis,s):
    if (s):
        data = CmdInterpreter.input()
        if data == "":
            jarvis.say("Sorry, an error occured", Fore.BLUE)
            return
        elif(data == "/ss") or (data == "/screenshot") or (data == "/capture") :
            jarvis.say("Please give me a moment", Fore.BLUE)
            incr += 1
            incr = str(incr) 
            myScreenshot = pyautogui.screenshot()
            myScreenshot.save(r'./../ss'+incr+'.png')
            if(os.path.isfile('./../ss'+incr+'.png')==False):
                jarvis.say("Success!", Fore.BLUE)
            else:
                jarvis.say("Sorry, an error occured retry using /ss , /screenshot, /capture", Fore.RED)
