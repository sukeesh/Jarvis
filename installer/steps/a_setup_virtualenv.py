import os
import re

from helper import *
import unix_windows


section("Preparing virtualenv")

# check that virtualenv installed
if not executable_exists('virtualenv'):
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
        # TODO Windows select python version
        shell("virtualenv env").should_not_fail()
    else:
        regex = re.compile("^python\\d?(\\.\\d*)?$")
        python_versions = os.listdir('/usr/bin/')
        python_versions = [(x, x) for x in python_versions if regex.match(x)]
        python_versions.append(("other", False))
        version = user_input(python_versions)
        if version is False:
            version = input("Python Executable: ")

        print("Selected python version {}".format(version))
        shell("virtualenv env --python={}".format(version)).should_not_fail()
