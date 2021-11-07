from helper import *
import unix_windows


section("Installing requirements")
CMD = "{} install -U -r installer/requirements.txt"
CMD = CMD.format(unix_windows.VIRTUALENV_PIP)
shell(CMD).should_not_fail()
