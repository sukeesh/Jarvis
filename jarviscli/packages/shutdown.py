# -*- coding: utf-8 -*-
import os


def shutdown_system():
    minutes = input('In how many minutes?: ')
    string = 'sudo shutdown -t ' + str(minutes)
    os.system(string)


def cancel_shutdown():
    os.system('sudo shutdown -c')
    print('Shutdown cancelled.')


def reboot_system():
    minutes = input('In how many minutes?: ')
    string = 'sudo shutdown -r -t ' + str(minutes)
    os.system(string)
