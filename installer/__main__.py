import os
import shutil
import sys

import helper

# Make sure that not running in virtualenv
if hasattr(sys, 'real_prefix'):
    helper.fail("""Please exit virtualenv!""")

# check that virtualenv on python3 installed
py3_installed = helper.shell("{} --version".format(helper.PY3))
if not py3_installed.success() or not py3_installed.cli_output.startswith('Python 3'):
    helper.fail("Please install Python3!\n")

py3venv_installed = helper.shell("{} --version".format(helper.VIRTUALENV_CMD))
if not py3venv_installed.success():
    venv_installed = helper.shell("virtualenv --version")

    if not venv_installed.success():
        print("Please install virtualenv!")
        print("https://github.com/pypa/virtualenv")
        print(helper.VIRTUALENV_INSTALL_MSG)
        print("")

    helper.fail(">>> Apparently virtualenv on Python3 ({}) does not work. Exiting!".format(
        helper.VIRTUALENV_CMD))

# Check if 'virtualenv' exists
virtualenv_exists = os.path.isdir("env")

# Check that virtualenv works + is Python 3
if virtualenv_exists:
    venv_version = helper.shell(
        "{} --version".format(helper.VIRTUALENV_PYTHON))

    if not venv_version.cli_output.startswith('Python 3'):
        print("WARNING: python --version returns {}".format(venv_version.cli_output))
        print("Recreating virtualenv...")

        shutil.rmtree("env")
        virtualenv_exists = False

# Create virtualenv if necessary
if not virtualenv_exists:
    helper.shell("{} env".format(helper.VIRTUALENV_CMD)).should_not_fail()


# install required packages
CMD = "{} install -U -r installer/requirements.txt"
CMD = CMD.format(helper.VIRTUALENV_PIP)
helper.shell(CMD).should_not_fail()

print("Jarvis is installed. Run with " + helper.START)
