import os
import sys
import distutils.spawn
import time
import subprocess
from threading import Thread
from tempfile import NamedTemporaryFile
from unix_windows import IS_WIN


# python 2/3 compatibility
try:
    input = raw_input
except NameError:
    pass


def executable_exists(name):
    binary_path = distutils.spawn.find_executable(name)
    return binary_path is not None and os.access(binary_path, os.X_OK)


debug_log = None


def log_init():
    global debug_log
    debug_log = NamedTemporaryFile(delete=False, mode="w")
    print("Logging to {}".format(debug_log.name))


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
        print("Please check logs at \"{}\". If you open a bug report, please include this file.".format(debug_log.name))
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
        printlog("{}) {}".format((x + 1), item[0]))

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


def shell(cmd):
    class Fail:
        def should_not_fail(self, msg=''):
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

    log("_" * 40)
    log("Shell: {}".format(cmd))
    spinning_cursor_start()

    cli_output = ''
    try:
        cli_output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
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
    log("Shell: Exit {}".format(str(exit_code)))
    log("-" * 40)
    log("")

    spinning_cursor_stop()
    time.sleep(0.5)
    sys.stdout.write(' \b')

    return exit_code
