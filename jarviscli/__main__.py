# -*- coding: utf-8 -*-
import Jarvis
import colorama
from sys import argv


def main():
    # enable color on windows
    colorama.init()
    # start Jarvis
    jarvis = Jarvis.Jarvis()
    command = " ".join(argv[1:]).strip()
    jarvis.executor(command)


if __name__ == '__main__':
    main()
