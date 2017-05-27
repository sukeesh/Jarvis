# -*- coding: utf-8 -*-
import os


def turn_off_screen():
    os.system('xset dpms force off')


def update_system():
    linux_distribution = int(raw_input("""
Select your distro:
[1] Ubuntu/Linux Mint/Debian
[2] Fedora
[3] Arch Linux

"""))
    if linux_distribution == 1:
        os.system('sudo apt-get update && sudo apt-get upgrade -y')

    elif linux_distribution == 2:
        os.system('dnf upgrade && dnf system-upgrade')

    elif linux_distribution == 3:
        has_yaourt = str.lower(raw_input("Do you have yaourt? (y/n)"))

        if has_yaourt == 'n':
            os.system('sudo pacman -Syu')

        elif has_yaourt == 'y':
            os.system('yaourt -Syyua --devel')

        else:
            print("You did not select a correct answer")
