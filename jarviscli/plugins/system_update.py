# -*- coding: utf-8 -*-
import os
import subprocess

from plugin import plugin, require, LINUX, MACOS


@require(platform=MACOS)
@plugin("update system")
def update_system__macos(jarvis, s):
    os.system('brew upgrade && brew update')


@require(platform=LINUX)
@require(native='lsb_release')
@plugin("update system")
def update_system(jarvis, s):
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
