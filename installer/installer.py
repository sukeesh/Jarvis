import os
import re
import sys

import optional
from helper import *
import unix_windows


# ==== PREPARE ===
log_init()
# Go to top level Jarvis folder
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ==== PREPARING VIRTUALENV ===
section("Preparing virtualenv")

# check that virtualenv installed
if not executable_exists('virtualenv'):
    fail("""\
Please install virtualenv!

https://github.com/pypa/virtualenv

{}""".format(VIRTUALENV_INSTALL_MSG))

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


# === PIP INSTALL PYTHON REQUIREMENTS ===
section("Install requirements")

shell("pip install -U -r installer/requirements.txt", True).should_not_fail()


# === NLTK DOWNLOAD ===
section("Download additional data (Dictionary)")

shell('python -m nltk.downloader -d jarviscli/data/nltk wordnet', True).should_not_fail()


# === OPTIONAL (NON-PYTHON) REQUIREMENTS
section("Check optional requirements")

requirements_failed = []


def check_optional_requirement(requirement):
    if 'pip' in requirement.keys():
        if shell("pip install -U {}".format(" ".join(requirement['pip'])), True).success():
            return True
        else:
            return False
    elif 'executable' in requirement.keys():
        requirement_ok = True
        for executable in requirement['executable']:
            if not executable_exists(executable):
                requirement_ok = False

        if requirement_ok:
            return True
        else:
            return False


for requirement in optional.OPTIONAL_REQUIREMENTS:
    if check_optional_requirement(requirement):
        printlog("* Success: {}".format(requirement['name']))
    else:
        printlog("* Fail: {}".format(requirement['name']))
        text = "{} - {}".format(requirement['name'], requirement['description'])
        requirements_failed.append((text, requirement))


if unix_windows.IS_WIN:
    # TODO Windows optional requirements?
    pass
else:
    section("Install *optional* non-python requirements")
    requirements_failed.append(("Install nothing", 'exit'))
    python_is_python_2 = shell("python --version 2>&1 | grep -q 'Python 2.'", True).success()

    while True:
        requirement = user_input(requirements_failed)
        print('')
        print('')
        if requirement == 'exit':
            break

        guess = None

        printlog(requirement['name'])
        printlog(requirement['instruction'])

        if 'package_guess' in requirement.keys():
            package = optional.get_guess(requirement['package_guess'])

            if package is not False:
                package_manager = optional.get_guess(optional.PackageManager)
                if python_is_python_2:
                    package = package[0]
                else:
                    package = package[1]
                cmd = "{} {}".format(package_manager, package)

                print("\nOur Guess how to install:\n>{}".format(cmd))
        print('')
        input('continue  ')
        print('')
        print('')
        print('')

        if check_optional_requirement(requirement):
            printlog('Success!')
            requirements_failed -= requirement
        else:
            printlog('Sorry; but looks like this did not work...')
        print('')


# write jarvis starter
# TODO Windows Install options?
if unix_windows.IS_WIN:
    fw = open('jarvis', 'w')
    fw.write("""\
@ECHO off
CALL {JARVISPATH}\env\Scripts\activate.bat
python {JARVISPATH}\jarviscli\
    """.format(JARVISPATH=os.getcwd()))
    printlog("Installation Successful! Use 'jarvis' in cmd to start Jarvis!")
else:

    section("Write Jarvis starter")

    JARVIS_MACRO = """\
    #!/bin/bash
    source {PATH}/env/bin/activate
    python {PATH}/jarviscli
    """

    fw = open('jarvis', 'w')
    fw.write(JARVIS_MACRO.format(PATH=os.getcwd()))
    fw.close()

    install_options = [("Install jarvis /usr/local/bin starter (requires root)", 0),
                       ("Add {} to $PATH (.bashrc)".format(os.getcwd()), 1),
                       ("Do nothing (Call Jarvis by full path)", 2)]
    selection = user_input(install_options)

    if selection == 0:
        os.system('sudo cp jarvis /usr/local/bin')
    elif selection == 1:
        os.system('export PATH=\\$PATH:{}" >> ~/.bashrc'.format(os.getcwd()))

    printlog('\n\nInstallation complete. Try unsing Jarvis!')
    if selection != 2:
        printlog('$ jarvis')
    else:
        printlog('$ {}/jarvis'.format(os.getcwd()))


log_close()
