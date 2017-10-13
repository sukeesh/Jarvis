# -*- coding: utf-8 -*-
import os
import subprocess

from utilities.GeneralUtilities import IS_MACOS


def turn_off_screen():
    if IS_MACOS:
        os.system('pmset displaysleepnow')
    else:
        os.system('xset dpms force off')


def update_system():
    if IS_MACOS:
        os.system('brew upgrade && brew update')
        return

    release = subprocess.check_output('cat /etc/lsb-rel' +
                                      'ease | grep' +
                                      ' DISTRIB_ID=', shell=True)
    get_line = release.split('=')

    user_distribution = get_line[1]
    print(user_distribution)
    if user_distribution == "Ubuntu\n" or user_distribution == "LinuxMint\n":
        os.system('sudo apt-get update && sudo apt-get upgrade -y')

    elif user_distribution == "Fedora\n":
        os.system('dnf upgrade && dnf system-upgrade')

    elif user_distribution == "Arch Linux\n":
        os.system('sudo pacman -Syu')
