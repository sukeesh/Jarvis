# -*- coding: utf-8 -*-
import sys

import colorama

import ui.CmdInterpreter
from jarvis import Jarvis
from language import default


def check_python_version():
    return sys.version_info[0] == 3


def main():
    language_parser = default.DefaultLanguageParser()
    jarvis = Jarvis(language_parser)
    cmd_interpreter = ui.CmdInterpreter.CmdInterpreter(jarvis)

    command = " ".join(sys.argv[1:]).strip()
    cmd_interpreter.executor(command)


if __name__ == '__main__':
    if check_python_version():
        main()
    else:
        print("Sorry! Only Python 3 supported.")
