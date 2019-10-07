import os
import re

from helper import *
import unix_windows


section("Preparing virtualenv")

# check that virtualenv installed
virtualenv_installed = False

if unix_windows.IS_WIN:
    virtualenv_installed = shell(unix_windows.VIRTUALENV_CMD + ' -h').success()
else:
    virtualenv_installed = executable_exists('virtualenv')


if not virtualenv_installed:
    fail("""\
Please install virtualenv!

https://github.com/pypa/virtualenv

{}""".format(unix_windows.VIRTUALENV_INSTALL_MSG))

# Make sure that not running in virtualenv
if hasattr(sys, 'real_prefix'):
    fail("""Please exit virtualenv!""")

# Check if 'env' already exists + is virtualenv
virtualenv_exists = False
if os.path.isdir("env"):
    if shell(unix_windows.VIRTUALENV_CMD).success():
        virtualenv_exists = True


# Create virtualenv if necessary
if not virtualenv_exists:
    if unix_windows.IS_WIN:
        shell("py -3 -m virtualenv env").should_not_fail()
    else:
        shell("virtualenv env --python=python3").should_not_fail()
