from helper import *
import unix_windows


section("Install requirements")
CMD = "{} install -U -r installer/requirements.txt"
CMD = CMD.format(unix_windows.VIRTUALENV_PIP)
shell(CMD).should_not_fail()

section("Download resource requirements")
res_requirements = open('installer/res_requirements.txt', 'r')
for res_name in res_requirements:
    CMD = unix_windows.VIRTUALENV_PIP_DOWNLOAD
    CMD = CMD + " " + res_name
    shell(CMD).should_not_fail()
res_requirements.close()
