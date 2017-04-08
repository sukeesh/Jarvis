# -*- coding: utf-8 -*-
import os

def turn_off_screen():
    os.system('xset dpms force off')

def update_system():
    os.system('sudo apt-get update && sudo apt-get upgrade -y')