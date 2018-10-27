# -*- coding: utf-8 -*-
import os
import subprocess

from utilities.GeneralUtilities import IS_MACOS


def update_system():
    if IS_MACOS:
        os.system('brew upgrade && brew update')
        return

    user_distributor_id = subprocess.check_output('lsb_release -i', shell=True)
    user_distribution = user_distributor_id.decode("utf-8").split('\t')[1]

    print(user_distribution)
    if user_distribution == "Ubuntu\n" or user_distribution == "LinuxMint\n":
        os.system('sudo apt-get update && sudo apt-get upgrade -y')

    elif user_distribution == "Fedora\n":
        os.system('dnf upgrade && dnf system-upgrade')

    elif user_distribution == "Arch Linux\n":
        os.system('sudo pacman -Syu')

    elif user_distribution == "openSUSE\n":
        os.system('sudo zypper update')
