import distutils.spawn
import os
import re
import sys
import time
from tempfile import NamedTemporaryFile
from threading import Thread

import optional

# python 2 / 3 compability
try:
    input = raw_input
except NameError:
    pass


debug_log = NamedTemporaryFile(delete=False)
print("Logging to {}".format(debug_log.name))


def fail(msg, fatal=False):
    log("Installation failed")
    log(msg)
    print(msg)
    print('')
    print('')
    if fatal:
        log("FATAL!")
        print("Installation failed with unexpected error - This should not have happend.")
        print("Please check logs at {}. If you open a bug report, please include this file.".format(debug_log.name))
    else:
        print("Installation failed!")
    debug_log.close()
    sys.exit(1)


def log(msg):
    debug_log.write(msg)
    debug_log.write('\n')


def printlog(msg):
    log(msg)
    print(msg)


def section(title):
    printlog("\n{:=^50}".format(" {} ".format(title)))


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

def executable_exists(name):
    binary_path = distutils.spawn.find_executable(name)
    return binary_path is not None and os.access(binary_path, os.X_OK)


def user_input(items):
    log("User input:")
    for x, item in enumerate(items):
        printlog("{}) {}".format((x+1), item[0]))

    while True:
        number = input("Select number {}-{}: ".format(1, len(items)))
        try:
            number = int(number) - 1
        except ValueError:
            log("> User input {} - not a number".format(number))
            continue

        if number >= 0 and number < len(items):
            log("> User input {} - ok: {}".format(number, items[number][1]))
            return items[number][1]
        else:
            log("> User input {} - out of range {} - {}".format(number, 1, len(items)))


def shell(cmd, run_in_virtualenv=False):
    log("Shell: {}; run_in_virtualenv: {}".format(cmd, run_in_virtualenv))
    spinning_cursor_start()
    if run_in_virtualenv:
        ret = os.system('source env/bin/activate && {} &>> {}'.format(cmd, debug_log.name))
    else:
        ret = os.system('{} &>> {}'.format(cmd, debug_log.name))
    spinning_cursor_stop()

    time.sleep(0.5)
    sys.stdout.write(' \b')
    log("Shell: Exit with status {}\n#################################\n\n".format(ret))

    class Fail:
        def should_not_fail(self, msg=''):
            fail(msg, fatal=True)

        def success(self):
            return False

    class Success:
        def should_not_fail(self, msg=''):
            pass

        def success(self):
            return True


    if ret == 0:
        return Success()
    else:
        return Fail()



section("Preparing virtualenv")

# check that virtualenv installed
if not executable_exists('virtualenv'):
    fail("""\
Please install virtualenv!

https://github.com/pypa/virtualenv

For Example on Ubuntu you could do
    > [sudo] apt install virtualenv
Or use Pip:
    > [sudo] pip install virtualenv"
""")

# Make sure that not running in virtualenv
if hasattr(sys, 'real_prefix'):
    fail("""Please exit virtualenv!""")

# Go to top level Jarvis folder
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if 'env' already exists + is virtualenv
virtualenv_exists = False
if os.path.isdir("env"):
    if shell("source env/bin/activate").success():
        virtualenv_exists = True

# Create virtualenv if necessary
if not virtualenv_exists:
    regex = re.compile("^python\\d?(\\.\\d*)?$")
    python_versions = os.listdir('/usr/bin/')
    python_versions = [ (x, x) for x in python_versions if regex.match(x) ]
    python_versions.append(("other", False))
    version = user_input(python_versions)
    if version is False:
        version = input("Python Version: ")

    print("Selected python version {}".format(version))
    shell("virtualenv env --python={}".format(version)).should_not_fail()


section("Install requirements")
shell("pip install -U -r installer/requirements.txt", True).should_not_fail()

# wordnet downloader
section("Download additional data (Dictionary)")
shell('python -m nltk.downloader -d jarviscli/data/nltk wordnet', True).should_not_fail()


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


section("Install optional requirements")
requirements_failed.append(('Exit', 'exit'))
python_is_python_2 = shell("python --version 2>&1 | grep -q 'Python 2.'", True).success()

while True:
    requirement = user_input(requirements_failed)
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
    input('continue')

    if check_optional_requirement(requirement):
        printlog('Success')
        requirements_failed -= requirement
    else:
        printlog('Sorry; looks like did not work')


# write jarvis starter
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
    os.system('export PATH=\$PATH:{}" >> ~/.bashrc'.format(os.getcwd()))

printlog('\n\nInstallation complete. Try unsing Jarvis!')
if selection != 2:
    printlog('$ jarvis')
else:
    printlog('$ {}/jarvis'.format(os.getcwd()))

debug_log.close()
