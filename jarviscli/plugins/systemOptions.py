import os
import subprocess
from platform import architecture, dist, release
from platform import system as sys

from archey import archey
from colorama import Fore

from plugin import LINUX, MACOS, plugin


@plugin(plattform=MACOS, native="pmset")
def screen_off__MAC(jarvis, s):
    """Turn of screen instantly"""
    os.system('pmset displaysleepnow')


@plugin(plattform=LINUX, native="xset")
def screen_off__LINUX(jarvis, s):
    """Turn of screen instantly"""
    os.system('xset dpms force off')


@plugin()
def Os(jarvis, s):
    """Displays information about your operating system"""
    jarvis.say('[!] Operating System Information', Fore.BLUE)
    jarvis.say('[*] ' + sys(), Fore.GREEN)
    jarvis.say('[*] ' + release(), Fore.GREEN)
    jarvis.say('[*] ' + dist()[0], Fore.GREEN)
    for _ in architecture():
        jarvis.say('[*] ' + _, Fore.GREEN)


@plugin()
def systeminfo(jarvis, s):
    """Display system information with distribution logo"""
    archey.main()
