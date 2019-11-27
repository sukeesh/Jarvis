# -*- coding: utf-8 -*-
import Jarvis
import colorama
import sys
import subprocess
import signal


def check_python_version():
    return sys.version_info[0] == 3


def run_jarvis():
    # enable color on windows
    colorama.init()
    # start Jarvis
    command = " ".join(sys.argv[1:]).strip().replace('--no-fork', '')
    skip_intro = False
    if '--skip-intro' in command:
        command = command.replace('--skip-intro', '')
        skip_intro = True

    jarvis = Jarvis.Jarvis(skip_intro)
    jarvis.executor(command)


def do_nothing(*args):
    pass


if __name__ == '__main__':
    if check_python_version():
        if len(sys.argv) > 1:
            run_jarvis()
        else:
            signal.signal(signal.SIGINT, do_nothing)
            skip_intro = ''
            while subprocess.run(["python", "jarviscli", "--no-fork", skip_intro]).returncode == 42:
                skip_intro = '--skip-intro'
    else:
        print("Sorry! Only Python 3 supported.")
