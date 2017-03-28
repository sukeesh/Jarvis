# -*- coding: utf-8 -*-
import os

def shutdown_system():
    minutes = input('In how many minutes: ')
    string = 'sudo shutdown -t ' + str(minutes)
    os.system(string)

def cancelShutdown():
    os.system('sudo shutdown -c')
    print('Shutdown cancelled.')