import os
from platform import architecture, mac_ver, release
from platform import system as sys

from colorama import Fore, Style

import distro
from plugin import Platform, plugin, require


@require(platform=Platform.MACOS, native="pmset")
@plugin('screen off')
def screen_off__MAC(jarvis, s):
    """Turn of screen instantly"""
    os.system('pmset displaysleepnow')


@require(platform=Platform.LINUX, native="xset")
@plugin('screen off')
def screen_off__LINUX(jarvis, s):
    """Turn of screen instantly"""
    os.system('xset dpms force off')


@require(platform=Platform.MACOS)
@plugin('os')
def Os__MAC(jarvis, s):
    """Displays information about your operating system"""
    jarvis.say(
        Style.BRIGHT
        + '[!] Operating System Information'
        + Style.RESET_ALL,
        Fore.BLUE)
    jarvis.say('[*] Kernel: ' + sys(), Fore.GREEN)
    jarvis.say('[*] Kernel Release Version: ' + release(), Fore.GREEN)
    jarvis.say('[*] macOS System version: ' + mac_ver()[0], Fore.GREEN)
    for _ in architecture():
        if _ != '':
            jarvis.say('[*] ' + _, Fore.GREEN)


@require(platform=[Platform.LINUX, Platform.WINDOWS])
@plugin('os')
def Os__LINUX(jarvis, s):
    """Displays information about your operating system"""
    jarvis.say('[!] Operating System Information', Fore.BLUE)
    jarvis.say('[*] ' + sys(), Fore.GREEN)
    jarvis.say('[*] ' + release(), Fore.GREEN)
    jarvis.say('[*] ' + distro.name(), Fore.GREEN)
    for _ in architecture():
        jarvis.say('[*] ' + _, Fore.GREEN)


@require(platform=Platform.LINUX)
@plugin('systeminfo')
def systeminfo__LINUX(jarvis, s):
    """Display system information with distribution logo"""
    from archey import archey
    archey.main()


@require(platform=Platform.MACOS, native="screenfetch")
@plugin('systeminfo')
def systeminfo__MAC(jarvis, s):
    """Display system information with distribution logo"""
    os.system("screenfetch")


@require(platform=Platform.WINDOWS)
@plugin('systeminfo')
def systeminfo_win(jarvis, s):
    """Display system infomation"""
    os.system("systeminfo")


@require(native="free", platform=Platform.UNIX)
@plugin("check ram")
def check_ram__UNIX(jarvis, s):
    """
    checks your system's RAM stats.
    -- Examples:
        check ram
    """
    os.system("free -lm")


@require(platform=Platform.WINDOWS)
@plugin("check ram")
def check_ram__WINDOWS(jarvis, s):
    """
    checks your system's RAM stats.
    -- Examples:
        check ram
    """
    import psutil
    mem = psutil.virtual_memory()

    def format(size):
        mb, _ = divmod(size, 1024 * 1024)
        gb, mb = divmod(mb, 1024)
        return "%s GB %s MB" % (gb, mb)
    jarvis.say("Total RAM: %s" % (format(mem.total)), Fore.BLUE)
    if mem.percent > 80:
        color = Fore.RED
    elif mem.percent > 60:
        color = Fore.YELLOW
    else:
        color = Fore.GREEN
    jarvis.say("Available RAM: %s" % (format(mem.available)), color)
    jarvis.say("RAM used: %s%%" % (mem.percent), color)
