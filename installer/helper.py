import os
import sys
import shutil
import time
import subprocess
from threading import Thread
from tempfile import NamedTemporaryFile

# python 2/3 compatibility
try:
    input = raw_input
except NameError:
    pass

SUPPORTED_SHELLS = ['bash', 'zsh']

def executable_exists(name):
    """
    Check if an executable exists and is accessible.
    Args:
        name (str): Name of the executable.
    Returns:
        bool: True if the executable exists, False otherwise.
    """
    binary_path = shutil.which(name)
    return binary_path is not None and os.access(binary_path, os.X_OK)

debug_log = None

def log_init():
    """
    Initialize a temporary file for logging.
    """
    global debug_log
    debug_log = NamedTemporaryFile(delete=False, mode="w")
    print(f"Logging to {debug_log.name}")

def log_close():
    """
    Close the log file.
    """
    debug_log.close()

def fail(msg, fatal=False):
    """
    Handle installation failures by logging and displaying the error message.
    Args:
        msg (str): Error message to display.
        fatal (bool): If True, indicates a fatal error.
    """
    log("Installation failed")
    log(msg)
    print(msg)
    if fatal:
        log("FATAL!")
        print("Installation failed with unexpected error.")
        print(f"Please check logs at \"{debug_log.name}\". If you open a bug report, include this file.")
    else:
        print("Installation failed!")
    debug_log.close()
    sys.exit(1)

def log(msg):
    """
    Write a message to the log file.
    Args:
        msg (str): Message to log.
    """
    try:
        debug_log.write(f"{msg}\n")
    except Exception as e:
        print(f"Logging failed: {e}")

def printlog(msg):
    """
    Log a message and print it to the console.
    Args:
        msg (str): Message to log and print.
    """
    log(msg)
    print(msg)

def section(title):
    """
    Print and log a section title.
    Args:
        title (str): Title of the section.
    """
    printlog(f"\n{'=' * 50}\n{title:^50}\n{'=' * 50}")

spinning = True

def spinning_cursor_start():
    """
    Start a spinning cursor in the console.
    """
    global spinning
    spinning = True

    def spin_start():
        while spinning:
            for cursor in '|/-\\':
                sys.stdout.write(cursor)
                sys.stdout.flush()
                time.sleep(0.1)
                sys.stdout.write('\b')

    Thread(target=spin_start).start()

def spinning_cursor_stop():
    """
    Stop the spinning cursor.
    """
    global spinning
    spinning = False

def user_input(items):
    """
    Prompt the user to select an item from a list.
    Args:
        items (list): List of tuples where each tuple contains a description and a value.
    Returns:
        value: The selected value.
    """
    log("User input:")
    for x, item in enumerate(items):
        printlog(f"{x + 1}) {item[0]}")

    while True:
        number = input(f"Select number 1-{len(items)}: ")
        try:
            number = int(number) - 1
        except ValueError:
            log(f"Invalid input: {number}")
            continue

        if 0 <= number < len(items):
            log(f"Selected: {items[number][1]}")
            return items[number][1]
        else:
            log(f"Input out of range: {number}")

def confirm_user_input(confirmation_message):
    """
    Prompt the user to confirm an action.
    Args:
        confirmation_message (str): Confirmation message to display.
    Returns:
        bool: True if the user confirms, False otherwise.
    """
    log("User Confirmation")
    printlog(confirmation_message)
    confirm = input("Input 'y' to confirm, 'n' to cancel: ").strip().lower()
    confirm_bool = confirm in ['y', 'yes']
    log(f"User chose to {'confirm' if confirm_bool else 'cancel'} the operation.")
    return confirm_bool

def shell(cmd):
    """
    Execute a shell command and return its result.
    Args:
        cmd (str): Shell command to execute.
    Returns:
        Success or Fail object depending on the command execution result.
    """
    class ShellResult:
        """
        Represents the result of a shell command.
        """
        def __init__(self, success, output='', exception=None):
            self.success = success
            self.output = output
            self.exception = exception

        def __str__(self):
            return "OK" if self.success else f"FAIL {self.exception}"

    log("_" * 40)
    log(f"Shell: {cmd}")
    spinning_cursor_start()

    result = ShellResult(success=True)
    try:
        result.output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        result.success = False
        result.exception = str(e)
        result.output += str(e.output)

    log(result.output)
    log(f"Shell: Exit {str(result)}")
    spinning_cursor_stop()
    return result

def get_default_shell():
    """
    Determine and return the default shell of the current logged-in user.
    Returns:
        str: Name of the default shell.
    """
    bin_path = os.environ.get('SHELL')
    return os.path.basename(bin_path) if bin_path else None
