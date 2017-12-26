# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2013  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
################################################################################

#
# ANSI codes abstraction borrowed from colorama and is covered by its own
# license. https://pypi.python.org/pypi/colorama

# Spinner and progress bar code modified from astropy and is covered by its own
# license. https://github.com/astropy/astropy
#

################################################################################
# Copyright (c) 2010 Jonathan Hartley <tartley@tartley.com>
# Copyright (c) 2011-2013, Astropy Developers
#
# Released under the New BSD license (reproduced below), or alternatively you may
# use this software under any OSI approved open source license such as those at
# http://opensource.org/licenses/alphabetical
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name(s) of the copyright holders, nor those of its contributors
#   may be used to endorse or promote products derived from this software without
#   specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
################################################################################
from __future__ import print_function
import os
import sys
import time
import types
import struct
from ..compat import PY2
from .. import LOCAL_ENCODING
from . import formatSize, formatTime
from .log import log

try:
    import fcntl
    import termios
    import signal
    _CAN_RESIZE_TERMINAL = True
except ImportError:
    _CAN_RESIZE_TERMINAL = False


class AnsiCodes(object):
    _USE_ANSI = False
    _CSI = '\033['

    def __init__(self, codes):
        def code_to_chars(code):
            return AnsiCodes._CSI + str(code) + 'm'

        for name in dir(codes):
            if not name.startswith('_'):
                value = getattr(codes, name)
                setattr(self, name, code_to_chars(value))

                # Add color function
                for reset_name in ("RESET_%s" % name, "RESET"):
                    if hasattr(codes, reset_name):
                        reset_value = getattr(codes, reset_name)
                        setattr(self, "%s" % name.lower(),
                                AnsiCodes._mkfunc(code_to_chars(value),
                                                  code_to_chars(reset_value)))
                        break

    @staticmethod
    def _mkfunc(color, reset):
        def _cwrap(text, *styles):
            if not AnsiCodes._USE_ANSI:
                return text

            s = u''
            for st in styles:
                s += st
            s += color + text + reset
            if styles:
                s += Style.RESET_ALL
            return s
        return _cwrap

    def __getattribute__(self, name):
        attr = super(AnsiCodes, self).__getattribute__(name)
        if (hasattr(attr, "startswith") and attr.startswith(AnsiCodes._CSI)
                and not AnsiCodes._USE_ANSI):
            return ''
        else:
            return attr

    def __getitem__(self, name):
        return getattr(self, name.upper())

    @staticmethod
    def init(enabled):
        if not enabled:
            AnsiCodes._USE_ANSI = False
        else:
            AnsiCodes._USE_ANSI = True
            if (("TERM" in os.environ and os.environ["TERM"] == "dumb") or
                ("OS" in os.environ and os.environ["OS"] == "Windows_NT")):
                AnsiCodes._USE_ANSI = False


class AnsiFore:
    GREY    = 30
    RED     = 31
    GREEN   = 32
    YELLOW  = 33
    BLUE    = 34
    MAGENTA = 35
    CYAN    = 36
    WHITE   = 37
    RESET   = 39

class AnsiBack:
    GREY    = 40
    RED     = 41
    GREEN   = 42
    YELLOW  = 43
    BLUE    = 44
    MAGENTA = 45
    CYAN    = 46
    WHITE   = 47
    RESET   = 49

class AnsiStyle:
    RESET_ALL         = 0
    BRIGHT            = 1
    RESET_BRIGHT      = 22
    DIM               = 2
    RESET_DIM         = RESET_BRIGHT
    ITALICS           = 3
    RESET_ITALICS     = 23
    UNDERLINE         = 4
    RESET_UNDERLINE   = 24
    BLINK_SLOW        = 5
    RESET_BLINK_SLOW  = 25
    BLINK_FAST        = 6
    RESET_BLINK_FAST  = 26
    INVERSE           = 7
    RESET_INVERSE     = 27
    STRIKE_THRU       = 9
    RESET_STRIKE_THRU = 29

Fore = AnsiCodes(AnsiFore)
Back = AnsiCodes(AnsiBack)
Style = AnsiCodes(AnsiStyle)


def ERROR_COLOR(): return   Fore.RED
def WARNING_COLOR(): return Fore.YELLOW
def HEADER_COLOR(): return  Fore.GREEN


class Spinner(object):
    """
    A class to display a spinner in the terminal.

    It is designed to be used with the `with` statement::

        with Spinner("Reticulating splines", "green") as s:
            for item in enumerate(items):
                s.next()
    """
    _default_unicode_chars = u"◓◑◒◐"
    _default_ascii_chars = u"-/|\\"

    def __init__(self, msg, file=None, step=1,
                 chars=None, use_unicode=True, print_done=True):

        self._msg = msg
        self._file = file or sys.stdout
        self._step = step
        if not chars:
            if use_unicode:
                chars = self._default_unicode_chars
            else:
                chars = self._default_ascii_chars
        self._chars = chars

        self._silent = not self._file.isatty()
        self._print_done = print_done

    def _iterator(self):
        chars = self._chars
        index = 0
        write = self._file.write
        flush = self._file.flush

        while True:
            write(u'\r')
            write(self._msg)
            write(u' ')
            write(chars[index])
            flush()
            yield

            for i in xrange(self._step):
                yield

            index += 1
            if index == len(chars):
                index = 0

    def __enter__(self):
        if self._silent:
            return self._silent_iterator()
        else:
            return self._iterator()

    def __exit__(self, exc_type, exc_value, traceback):
        write = self._file.write
        flush = self._file.flush

        if not self._silent:
            write(u'\r')
            write(self._msg)
        if self._print_done:
            if exc_type is None:
                write(Fore.GREEN + u' [Done]\n')
            else:
                write(Fore.RED + u' [Failed]\n')
        else:
            write("\n")
        flush()

    def _silent_iterator(self):
        self._file.write(self._msg)
        self._file.flush()

        while True:
            yield

class ProgressBar(object):
    """
    A class to display a progress bar in the terminal.

    It is designed to be used either with the `with` statement::

        with ProgressBar(len(items)) as bar:
            for item in enumerate(items):
                bar.update()

    or as a generator::

        for item in ProgressBar(items):
            item.process()
    """
    def __init__(self, total_or_items, file=None):
        """
        Parameters
        ----------
        total_or_items : int or sequence
            If an int, the number of increments in the process being
            tracked.  If a sequence, the items to iterate over.

        file : writable file-like object, optional
            The file to write the progress bar to.  Defaults to
            `sys.stdout`.  If `file` is not a tty (as determined by
            calling its `isatty` member, if any), the scrollbar will
            be completely silent.
        """
        self._file = file or sys.stdout

        if not self._file.isatty():
            self.update = self._silent_update
            self._silent = True
        else:
            self._silent = False

        try:
            self._items = iter(total_or_items)
            self._total = len(total_or_items)
        except TypeError:
            try:
                self._total = int(total_or_items)
                self._items = iter(xrange(self._total))
            except TypeError:
                raise TypeError("First argument must be int or sequence")

        self._start_time = time.time()

        self._should_handle_resize = (
            _CAN_RESIZE_TERMINAL and self._file.isatty())
        self._handle_resize()
        if self._should_handle_resize:
            signal.signal(signal.SIGWINCH, self._handle_resize)
            self._signal_set = True
        else:
            self._signal_set = False

        self.update(0)

    def _handle_resize(self, signum=None, frame=None):
        if self._should_handle_resize:
            data = fcntl.ioctl(self._file, termios.TIOCGWINSZ, '\0' * 8)
            terminal_width = struct.unpack("HHHH", data)[1]
        else:
            try:
                terminal_width = int(os.environ.get('COLUMNS'))
            except (TypeError, ValueError):
                terminal_width = 78
        self._terminal_width = terminal_width

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self._silent:
            if exc_type is None:
                self.update(self._total)
            self._file.write('\n')
            self._file.flush()
            if self._signal_set:
                signal.signal(signal.SIGWINCH, signal.SIG_DFL)

    def __iter__(self):
        return self

    def next(self):
        try:
            rv = next(self._items)
        except StopIteration:
            self.__exit__(None, None, None)
            raise
        else:
            self.update()
            return rv

    def update(self, value=None):
        """
        Update the progress bar to the given value (out of the total
        given to the constructor).
        """
        if value is None:
            value = self._current_value = self._current_value + 1
        else:
            self._current_value = value
        if self._total == 0:
            frac = 1.0
        else:
            frac = float(value) / float(self._total)

        file = self._file
        write = file.write

        suffix = self._formatSuffix(value, frac)
        self._bar_length = self._terminal_width - 37

        bar_fill = int(float(self._bar_length) * frac)
        write(u'\r|')
        write(Fore.BLUE + u'=' * bar_fill + Fore.RESET)
        if bar_fill < self._bar_length:
            write(Fore.GREEN + u'>' + Fore.RESET)
            write(u'-' * (self._bar_length - bar_fill - 1))
        write(u'|')
        write(suffix)

        self._file.flush()

    def _formatSuffix(self, value, frac):

        if value >= self._total:
            t = time.time() - self._start_time
            time_str = '     '
        elif value <= 0:
            t = None
            time_str = ''
        else:
            t = ((time.time() - self._start_time) * (1.0 - frac)) / frac
            time_str = u' ETA '
        if t is not None:
            time_str += formatTime(t, short=True)

        suffix = ' {0:>4s}/{1:>4s}'.format(formatSize(value, short=True),
                                           formatSize(self._total, short=True))
        suffix += u' ({0:>6s}%)'.format(u'{0:.2f}'.format(frac * 100.0))
        suffix += time_str

        return suffix

    def _silent_update(self, value=None):
        pass

    @classmethod
    def map(cls, function, items, multiprocess=False, file=None):
        """
        Does a `map` operation while displaying a progress bar with
        percentage complete.

        ::

            def work(i):
                print(i)

            ProgressBar.map(work, range(50))

        Parameters
        ----------
        function : function
            Function to call for each step

        items : sequence
            Sequence where each element is a tuple of arguments to pass to
            *function*.

        multiprocess : bool, optional
            If `True`, use the `multiprocessing` module to distribute each
            task to a different processor core.

        file : writeable file-like object, optional
            The file to write the progress bar to.  Defaults to
            `sys.stdout`.  If `file` is not a tty (as determined by
            calling its `isatty` member, if any), the scrollbar will
            be completely silent.
        """
        results = []

        if file is None:
            file = stdio.stdout

        with cls(len(items), file=file) as bar:
            step_size = max(200, bar._bar_length)
            steps = max(int(float(len(items)) / step_size), 1)
            if not multiprocess:
                for i, item in enumerate(items):
                    function(item)
                    if (i % steps) == 0:
                        bar.update(i)
            else:
                import multiprocessing
                p = multiprocessing.Pool()
                for i, result in enumerate(
                    p.imap_unordered(function, items, steps)):
                    bar.update(i)
                    results.append(result)

        return results


def _encode(s):
    '''This is a helper for output of unicode. With Python2 it is necessary to
    do encoding to the LOCAL_ENCODING since by default unicode will be encoded
    to ascii. In python3 this conversion is not necessary for the user to
    to perform; in fact sys.std*.write, for example, requires unicode strings
    be passed in. This function will encode for python2 and do nothing
    for python3 (except assert that ``s`` is a unicode type).'''
    if PY2:
        if isinstance(s, unicode):
            try:
                return s.encode(LOCAL_ENCODING)
            except Exception as ex:
                log.error("Encoding error: " + str(ex))
                return s.encode(LOCAL_ENCODING, "replace")
        elif isinstance(s, str):
            return s
        else:
            raise TypeError("Argument must be str or unicode")
    else:
        assert(isinstance(s, str))
        return s


def printMsg(s):
    fp = sys.stdout
    s = _encode(s)
    fp.write("%s\n" % s)
    fp.flush()


def printError(s):
    _printWithColor(s, ERROR_COLOR(), sys.stderr)


def printWarning(s):
    _printWithColor(s, WARNING_COLOR(), sys.stdout)


def printHeader(s):
    _printWithColor(s, HEADER_COLOR(), sys.stdout)


def boldText(s, fp=sys.stdout, c=None):
    return (Style.BRIGHT + (c or '') +
            s +
            (Fore.RESET if c else '') + Style.RESET_BRIGHT)


def _printWithColor(s, color, file):
    s = _encode(s)
    file.write(color + s + Fore.RESET + '\n')
    file.flush()


if __name__ == "__main__":
    AnsiCodes.init(True)

    def checkCode(c):
        return (c[0] != '_' and
                "RESET" not in c and
                c[0] == c[0].upper()
               )

    for bg_name, bg_code in ((c, getattr(Back, c))
                             for c in dir(Back) if checkCode(c)):
        sys.stdout.write('%s%-7s%s %s ' %
                         (bg_code, bg_name, Back.RESET, bg_code))
        for fg_name, fg_code in ((c, getattr(Fore, c))
                                 for c in dir(Fore) if checkCode(c)):
            sys.stdout.write(fg_code)
            for st_name, st_code in ((c, getattr(Style, c))
                                     for c in dir(Style) if checkCode(c)):
                sys.stdout.write('%s%s %s %s' %
                                 (st_code, st_name,
                                  getattr(Style, "RESET_%s" % st_name),
                                  bg_code))
        sys.stdout.write("%s\n" % Style.RESET_ALL)

    sys.stdout.write("\n")

    import time
    with Spinner(Fore.GREEN + u"Phase #1") as spinner:
        for i in range(50):
            time.sleep(.05)
            spinner.next()
    with Spinner(Fore.RED + u"Phase #2" + Fore.RESET,
                 print_done=False) as spinner:
        for i in range(50):
            time.sleep(.05)
            spinner.next()
    with Spinner(u"Phase #3", print_done=False, use_unicode=False) as spinner:
        for i in range(50):
            spinner.next()
            time.sleep(.05)
    with Spinner(u"Phase #4", print_done=False, chars='.oO°Oo.') as spinner:
        for i in range(50):
            spinner.next()
            time.sleep(.05)


    items = range(200)
    with ProgressBar(len(items)) as bar:
        for item in enumerate(items):
            bar.update()
            time.sleep(.05)

    for item in ProgressBar(items):
        time.sleep(.05)

    progress = 0
    max = 320000000
    with ProgressBar(max) as bar:
        while progress < max:
            progress += 23400
            bar.update(progress)
            time.sleep(.001)


