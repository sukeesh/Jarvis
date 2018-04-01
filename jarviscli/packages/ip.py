# -*- coding: utf-8 -*-
from utilities.GeneralUtilities import print_say
from colorama import Fore
from os import system

local_ip = """ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' |
            grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'"""

public_ip = "timeout 10 curl ifconfig.co"  # 10 second time out if not connected to internet


def get_local_ip(self):
    print_say("List of local ip addresses :", self, Fore.BLUE)
    system(local_ip)


def get_public_ip(self):
    print_say("Public ip address :", self, Fore.BLUE)
    system(public_ip)
