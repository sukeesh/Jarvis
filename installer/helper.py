import os
import sys
import shutil
import time
import subprocess
from threading import Thread
from tempfile import NamedTemporaryFile
from unix_windows import IS_WIN

SUPPORTED_SHELLS = [
    'bash',
    'zsh',
]

# python 2/3 compatibility
try:
    input = raw_input
except NameError:
    pass


def executable_exists(name):
    binary_path = shutil.which(name)
    return binary_path is not None and os.access(binary_path, os.X_OK)


debug_log = None


def log_init():
    global debug_log
    debug_log = NamedTemporaryFile(delete=False, mode="w")
    print(f"Logging to {debug_log.name}")


def log_close():
    debug_log.close()


def fail(msg, fatal=False):
    log("Installation failed")
    log(msg)
    print(msg)
    print('')
    print('')
    if fatal:
        log("FATAL!")
        print("Installation failed with unexpected error - This should not have happened.")
        print(f"""Please check logs at {debug_log.name}. 
              If you open a bug report, please include this file.""")
    else:
        print("Installation failed!")
    debug_log.close()
    sys.exit(1)


def log(msg):
    try:
        debug_log.write(msg)
        debug_log.write('\n')
    except Exception as e:
        print('------------------------------')
        print("Logging failed?")
        print(repr(e))
        print(str(e))
        print(str(e.args))
        print('msg:')
        try:
            print(str(msg))
        except BaseException:
            print('msg unprintable')
        print('-----------------------------')


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


def user_input(items):
    log("User input:")
    for x, item in enumerate(items):
        printlog(f"{x + 1}) {item[0]}")

    while True:
        number = input(f"Select number 1-{len(items)}: ")
        try:
            number = int(number) - 1
        except ValueError:
            log(f"> User input {number} - not a number")
            continue

        if number >= 0 and number < len(items):
            log(f"> User input {number} - ok: {items[number][1]}")
            return items[number][1]
        
        log(f"> User input {number} - out of range 1-{len(items)}")

def confirm_user_input(confirmation_message : str) -> bool:
    log("User Confirmation")
    printlog(confirmation_message)
    confirm = input("input 'y' to confirm, 'n' to cancel: ")
    confirm_bool = True if confirm in ['y', 'Y', 'yes', 'YES'] else False
    log(f"> User input {confirm} - {'confirm' if confirm_bool else 'cancel'}")
    return confirm_bool

def shell(cmd):
    class Fail:
        def should_not_fail(self, msg=''):
            fail(msg, fatal=True)

        def success(self):
            return False

        def __str__(self):
            return f"Fail {self.exception}"
    class Success:
        def should_not_fail(self, msg=''):
            pass

        def success(self):
            return True

        def __str__(self):
            return "OK"

    exit_code = Success()

    log("_" * 40)
    log(f"Shell: {cmd}")
    spinning_cursor_start()

    cli_output = ''
    try:
        cli_output = subprocess.check_output(cmd, shell=True, 
                                             stderr=subprocess.STDOUT, universal_newlines=True)
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

    log(cli_output)
    log(f"Shell: Exit {str(exit_code)}")
    log("-" * 40)
    log("")

    spinning_cursor_stop()
    time.sleep(0.5)
    sys.stdout.write(' \b')

    return exit_code


def get_default_shell():
    '''
    Determine and return the default shell
    of the current logged in user.
    Args:
        None
    Returns:
        shell name (str)
    '''
    try:
        bin_path = os.environ.get('SHELL')
        return bin_path.split(os.path.sep)[-1]
    except AttributeError:
        # SHELL environment not set
        return None
