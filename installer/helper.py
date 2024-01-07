import os
import sys
import shutil
import time
import subprocess
from threading import Thread
from tempfile import NamedTemporaryFile
from unix_windows import IS_WIN

SUPPORTED_SHELLS = ['bash', 'zsh']

class Logger:
    def __init__(self):
        self.debug_log = None

    def init_log(self):
        self.debug_log = NamedTemporaryFile(delete=False, mode="w")
        print(f"Logging to {self.debug_log.name}")

    def log(self, msg):
        try:
            self.debug_log.write(f"{msg}\n")
        except Exception as e:
            self.print_log('------------------------------')
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

    def print_log(self, msg):
        self.log(msg)
        print(msg)

    def close_log(self):
        self.debug_log.close()

logger = Logger()

def fail(msg, fatal=False):
    logger.print_log("Installation failed")
    logger.log(msg)
    print(msg)
    print('')
    print('')
    if fatal:
        logger.log("FATAL!")
        print("Installation failed with an unexpected error. This should not have happened.")
        print(f"Please check logs at \"{logger.debug_log.name}\". If you open a bug report, please include this file.")
    else:
        print("Installation failed!")
    logger.close_log()
    sys.exit(1)

def section(title):
    logger.print_log(f"\n{'{:=^50}'.format(f' {title} ')}")

def spinning_cursor_start():
    def spin_start():
        time.sleep(0.1)
        while getattr(spinning_cursor_start, "spinning", True):
            for cursor in '|/-\\':
                sys.stdout.write(cursor)
                sys.stdout.flush()
                time.sleep(0.1)
                sys.stdout.write('\b')

    Thread(target=spin_start).start()

def spinning_cursor_stop():
    spinning_cursor_start.spinning = False

def user_input(items):
    logger.log("User input:")
    for x, item in enumerate(items):
        logger.print_log(f"{x + 1}) {item[0]}")

    while True:
        number = input(f"Select number 1-{len(items)}: ")
        try:
            number = int(number) - 1
        except ValueError:
            logger.log(f"> User input {number} - not a number")
            continue

        if 0 <= number < len(items):
            logger.log(f"> User input {number} - ok: {items[number][1]}")
            return items[number][1]
        else:
            logger.log(f"> User input {number} - out of range 1 - {len(items)}")

 

def shell(cmd):
    class ShellException(Exception):
        pass

    logger.log("_" * 40)
    logger.log(f"Shell: {cmd}")
    spinning_cursor_start()

    cli_output = ''
    try:
        cli_output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        raise ShellException(str(e), output=str(e.output))

 
    try:
        cli_output = cli_output.decode("utf-8")
    except AttributeError:
        pass

    logger.log(cli_output)
    logger.log(f"Shell: Exit OK")
    logger.log("-" * 40)
    logger.log("")

    spinning_cursor_stop()
    time.sleep(0.5)
    sys.stdout.write(' \b')

    return cli_output

def get_default_shell():
    try:
        bin_path = os.environ.get('SHELL')
        return bin_path.split(os.path.sep)[-1]
    except AttributeError:
        return None

if __name__ == "__main__":
    try:
        logger.init_log()
       
    except ShellException as se:
        fail(f"Shell command failed: {se}", fatal=True)
    except Exception as e:
        fail(f"An unexpected error occurred: {e}", fatal=True)
    finally:
        logger.close_log()
