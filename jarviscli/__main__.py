# -*- coding: utf-8 -*-
import Jarvis
import colorama
import sys
from jarviscli.plugins.message import send_join_message


def check_python_version():
    return sys.version_info[0] == 3


def main():
    # enable color on windows
    colorama.init()
    # start Jarvis
    jarvis = Jarvis.Jarvis()

    # Send Telegram message on startup
    send_join_message()

    command = " ".join(sys.argv[1:]).strip()
    jarvis.executor(command)


if __name__ == '__main__':
    if check_python_version():
        main()
    else:
        print("Sorry! Only Python 3 supported.")
