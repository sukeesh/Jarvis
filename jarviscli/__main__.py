# -*- coding: utf-8 -*-
import Jarvis
from sys import argv


def main():
    jarvis = Jarvis.Jarvis()
    command = " ".join(argv[1:]).strip()
    jarvis.executor(command)


if __name__ == '__main__':
    main()
