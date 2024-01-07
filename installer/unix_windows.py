import os

def get_system_commands():
    is_windows = os.name == 'nt'

    if is_windows:
        if os.system('py --version') == 0:
            py3_cmd = "py -3"
            virtualenv_cmd = "py -3 -m virtualenv"
        else:
            py3_cmd = "python"
            virtualenv_cmd = "python -m virtualenv"
        virtualenv_python = "env\\Scripts\\python.exe"
        virtualenv_pip = "env\\Scripts\\pip.exe"
        virtualenv_install_msg = f"""\
    Note that virtualenv must work with Python 3!

    You could do:
    {py3_cmd} -m ensurepip
    {py3_cmd} -m pip install virtualenv
    """

    else:
        py3_cmd = "python3"
        virtualenv_cmd = "virtualenv --python=python3"
        virtualenv_python = "env/bin/python"
        virtualenv_pip = "env/bin/pip"
        virtualenv_install_msg = """\
    For example on Ubuntu you could do
        > [sudo] apt install virtualenv
    Or use Pip:
        > [sudo] pip install virtualenv
    """

    return py3_cmd, virtualenv_cmd, virtualenv_python, virtualenv_pip, virtualenv_install_msg

PY3, VIRTUALENV_CMD, VIRTUALENV_PYTHON, VIRTUALENV_PIP, VIRTUALENV_INSTALL_MSG = get_system_commands()
