import os

from jarviscli import entrypoint


@entrypoint
def go_to(jarvis, s):
    os.system("wmctrl -a " + s)  # switch to already opened app/software.
