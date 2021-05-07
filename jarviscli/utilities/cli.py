#######################################
# BASED ON
# https://pypi.org/project/inputimeout/
# (c) MitsuoHeijo
# License: MIT License (MIT)
######################################

import os
import sys

SP = ' '
CR = '\r'
LF = '\n'
CRLF = CR + LF


class TimeoutOccurred(Exception):
    pass


input_cancel = False
DEFAULT_TIMEOUT = 10


def echo(string):
    if len(string) != 0:
        sys.stdout.write(string)
        sys.stdout.flush()


def posix_inputimeout(timeout):
    sel = selectors.DefaultSelector()
    sel.register(sys.stdin, selectors.EVENT_READ)
    events = sel.select(timeout)

    if events:
        key, _ = events[0]
        return key.fileobj.readline().rstrip(LF)
    else:
        raise TimeoutOccurred


def win_inputimeout(timeout):
    begin = time.monotonic()
    end = begin + timeout
    line = ''

    while time.monotonic() < end:
        if msvcrt.kbhit():
            c = msvcrt.getwche()
            if c in (CR, LF):
                echo(CRLF)
                return line
            if c == '\003':
                raise KeyboardInterrupt
            if c == '\b':
                line = line[:-1]
            else:
                line += c
        time.sleep()

    raise TimeoutOccurred


try:
    import msvcrt

except ImportError:
    import selectors
    import termios

    inputimeout = posix_inputimeout

else:
    import time

    inputimeout = win_inputimeout


def input(prompt=""):
    if (prompt != ''):
        print(prompt)

    while input_cancel is False:
        try:
            return inputimeout(timeout=2)
        except TimeoutOccurred:
            pass
    return ''


def cancel():
    global input_cancel
    input_cancel = True


class HiddenPrints:
    """
    Thanks
    https://stackoverflow.com/questions/57012725/how-can-i-hide-all-text-output-in-pyttsx3
    """

    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        self._original_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        sys.stderr.close()
        sys.stderr = self._original_stderr
