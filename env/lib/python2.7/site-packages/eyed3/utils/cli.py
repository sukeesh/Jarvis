# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2011  Travis Shirk <travis@pobox.com>
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
'''
    This module is deprecated. Use eyed3.utils and eyed3.utils.console instead.
'''
import warnings
warnings.warn(__doc__, DeprecationWarning, stacklevel=2)
import sys
from collections import defaultdict
from .. import utils

# Importing for backawards compat
from ..utils import ArgumentParser, LoggingAction

RESET           = '\033[0m'
BOLD            = '\033[1m'
BOLD_OFF        = '\033[22m'
REVERSE         = '\033[2m'
ITALICS         = '\033[3m'
ITALICS_OFF     = '\033[23m'
UNDERLINE       = '\033[4m'
UNDERLINE_OFF   = '\033[24m'
BLINK_SLOW      = '\033[5m'
BLINK_SLOW_OFF  = '\033[25m'
BLINK_FAST      = '\033[6m'
BLINK_FAST_OFF  = '\033[26m'
INVERSE         = '\033[7m'
INVERSE_OFF     = '\033[27m'
STRIKE_THRU     = '\033[9m'
STRIKE_THRU_OFF = '\033[29m'

GREY      = '\033[30m'
RED       = '\033[31m'
GREEN     = '\033[32m'
YELLOW    = '\033[33m'
BLUE      = '\033[34m'
MAGENTA   = '\033[35m'
CYAN      = '\033[36m'
WHITE     = '\033[37m'

GREYBG    = '\033[40m'
REDBG     = '\033[41m'
GREENBG   = '\033[42m'
YELLOWBG  = '\033[43m'
BLUEBG    = '\033[44m'
MAGENTABG = '\033[45m'
CYANBG    = '\033[46m'
WHITEBG   = '\033[47m'

ERROR_COLOR   = RED
WARNING_COLOR = YELLOW
HEADER_COLOR  = GREEN

# Set this to disable terminal color codes
__ENABLE_COLOR_OUTPUT = defaultdict(bool)
__ENABLE_COLOR_OUTPUT[sys.stdout] = True
__ENABLE_COLOR_OUTPUT[sys.stderr] = True

def getColor(color_code, fp=sys.stdout):
    warnings.warn("Use eyed3.utils.console new color syntax",
                  stacklevel=2)
    if __ENABLE_COLOR_OUTPUT[fp]:
        return color_code or b""
    else:
        return b""

def enableColorOutput(fp, state=True):
    warnings.warn("Use eyed3.utils.console", DeprecationWarning,
                  stacklevel=2)
    global __ENABLE_COLOR_OUTPUT
    __ENABLE_COLOR_OUTPUT[fp] = bool(state)

@utils.encodeUnicode()
def printError(s):
    warnings.warn("Use eyed3.utils.console.printError", DeprecationWarning,
                  stacklevel=2)
    fp = sys.stderr
    fp.write('%s%s%s\n' % (getColor(ERROR_COLOR, fp), s, getColor(RESET, fp)))
    fp.flush()

@utils.encodeUnicode()
def printWarning(s):
    warnings.warn("Use eyed3.utils.console.printWarning", DeprecationWarning,
                  stacklevel=2)
    fp = sys.stderr
    fp.write('%s%s%s\n' % (getColor(WARNING_COLOR, fp), s, getColor(RESET, fp)))
    fp.flush()

@utils.encodeUnicode()
def printMsg(s):
    warnings.warn("Use eyed3.utils.console.printMsg", DeprecationWarning,
                  stacklevel=2)
    fp = sys.stdout
    fp.write("%s\n" % s)
    fp.flush()

@utils.encodeUnicode()
def printHeader(s):
    warnings.warn("Use eyed3.utils.console.printHeader", DeprecationWarning,
                  stacklevel=2)
    fp = sys.stdout
    fp.write('%s%s%s\n' % (getColor(HEADER_COLOR, fp), s, getColor(RESET, fp)))
    fp.flush()

@utils.encodeUnicode()
def boldText(s, fp=sys.stdout, c=None):
    warnings.warn("Use eyed3.utils.console new color syntax",
                  DeprecationWarning, stacklevel=2)
    return "%s%s%s%s" % (getColor(BOLD, fp), getColor(c, fp),
                         s, getColor(RESET, fp))

@utils.encodeUnicode()
def colorText(s, fp=sys.stdout, c=None):
    warnings.warn("Use eyed3.utils.console new color syntax",
                  stacklevel=2)
    return getColor(c, fp) + s + getColor(RESET)

