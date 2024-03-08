import os
import shutil
import subprocess
import sys
import time
import traceback
from tempfile import NamedTemporaryFile
from threading import Thread

# Read environment
if os.name == 'nt':
    IS_WIN = True
else:
    IS_WIN = False


if IS_WIN:
    if os.system('py --version') == 0:
        PY3 = "py -3"
        VIRTUALENV_CMD = "py -3 -m virtualenv"
    else:
        PY3 = "python"
        VIRTUALENV_CMD = "python -m virtualenv"
    VIRTUALENV_PYTHON = "env\\Scripts\\python.exe"
    VIRTUALENV_PIP = "env\\Scripts\\pip.exe"
    VIRTUALENV_INSTALL_MSG = """\
Note that virtualenv must work with Python 3!

You could do:
{PY3} -m ensurepip
{PY3} -m pip install virtualenv
""".format(PY3=PY3)
    START = "jarvis.sh"

else:
    PY3 = "python3"
    VIRTUALENV_CMD = "virtualenv --python=python3"
    VIRTUALENV_PYTHON = "env/bin/python"
    VIRTUALENV_PIP = "env/bin/pip"
    VIRTUALENV_INSTALL_MSG = """\
For example on Ubuntu you could do
    > [sudo] apt install virtualenv
Or use Pip:
    > [sudo] pip install virtualenv
"""
    START = "jarvis.bat"


def executable_exists(name):
    binary_path = shutil.which(name)
    return binary_path is not None and os.access(binary_path, os.X_OK)


def fail(msg, fatal=False):
    print(msg)
    print('')
    print('')
    if fatal:
        print("Installation failed with unexpected error - This should not have happened.")
    else:
        print("Installation failed!")
    sys.exit(1)


spinning = True


def spinning_cursor_start():
    global spinning
    spinning = True

    def spin_start():
        time.sleep(0.1)
        while spinning:
            for cursor in '|/-\\':
                sys.stdout.write(cursor)
                sys.stdout.flush()
                time.sleep(0.1)
                sys.stdout.write('\b')

    Thread(target=spin_start).start()


def spinning_cursor_stop():
    global spinning
    spinning = False


def shell(cmd):
    class Fail:
        def should_not_fail(self, msg=''):
            print(self)
            fail(msg, fatal=True)

        def success(self):
            return False

        def __str__(self):
            return "FAIL {}".format(self.exception)

    class Success:
        def should_not_fail(self, msg=''):
            pass

        def success(self):
            return True

        def __str__(self):
            return "OK"

    exit_code = Success()

    spinning_cursor_start()

    cli_output = ''
    try:
        cli_output = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        exit_code = Fail()
        exit_code.exception = str(e)
        cli_output += str(e.output)

    # python 2 compatibility
    try:
        cli_output = cli_output.decode("utf-8")
    except AttributeError:
        pass
    exit_code.cli_output = cli_output

    spinning_cursor_stop()
    time.sleep(0.5)
    sys.stdout.write(' \b')

    return exit_code
