from os import system
from time import ctime
from colorama import Fore
from plugin import plugin, require


@plugin('clock')
def clock(jarvis, s):
    """Gives information about time"""
    jarvis.say(ctime(), Fore.BLUE)


@require(native='termdown')
@plugin('stopwatch')
def stopwatch(jarvis, s):
    """
    Start stopwatch

    L       Lap
    R       Reset
    SPACE   Pause
    Q       Quit
    """
    system("termdown")


@require(native="termdown")
@plugin('timer')
def timer(jarvis, s):
    """
    Set a timer

    R       Reset
    SPACE   Pause
    Q       Quit

    Usages:

    timer 10
    timer 1h5m30s
    """
    k = s.split(' ', 1)
    if k[0] == '':
        jarvis.say("Please specify duration")
        return
    timer_cmd = "termdown " + k[0]
    system(timer_cmd)
