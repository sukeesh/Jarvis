import os
import shutil
import re

from helper import *
import unix_windows


section("Preparing virtualenv")

# Make sure that not running in virtualenv
if hasattr(sys, 'real_prefix'):
    fail("""Please exit virtualenv!""")

# check that virtualenv on python3 installed
py3_installed = shell("{} --version".format(unix_windows.PY3))
if not py3_installed.success() or not py3_installed.cli_output.startswith('Python 3'):
    fail("Please install Python3!\n")

py3venv_installed = shell("{} --version".format(unix_windows.VIRTUALENV_CMD))
if not py3venv_installed.success():
    venv_installed = shell("virtualenv --version")

    if not venv_installed.success():
        printlog("Please install virtualenv!")
        printlog("https://github.com/pypa/virtualenv")
        printlog(unix_windows.VIRTUALENV_INSTALL_MSG)
        printlog("")

    fail(">>> Apparently virtualenv on Python3 ({}) does not work. Exiting!".format(unix_windows.VIRTUALENV_CMD))

# Check if 'virtualenv' exists
virtualenv_exists = os.path.isdir("env")

# Check that virtualenv works + is Python 3
if virtualenv_exists:
    venv_version = shell("{} --version".format(unix_windows.VIRTUALENV_PYTHON))
    if not venv_version.cli_output.startswith('Python 3'):
        log("WARNING: python --version returns {}".format(venv_version.cli_output))

        printlog("Recreating virtualenv...")
        shutil.rmtree("env")
        virtualenv_exists = False

# Create virtualenv if necessary
if not virtualenv_exists:
    shell("{} env".format(unix_windows.VIRTUALENV_CMD)).should_not_fail()
