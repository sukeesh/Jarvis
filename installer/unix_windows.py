import os

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
