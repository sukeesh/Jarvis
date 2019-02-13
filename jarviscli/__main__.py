# -*- coding: utf-8 -*-
import Jarvis
import colorama


def main():
    # enable color on windows
    colorama.init()
    # start Jarvis
    jarvis = Jarvis.Jarvis()
    jarvis.executor()


if __name__ == '__main__':
    main()
