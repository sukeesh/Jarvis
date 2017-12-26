# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2002-2015  Travis Shirk <travis@pobox.com>
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
import logging

logging.basicConfig()

DEFAULT_FORMAT = '%(name)s:%(levelname)s: %(message)s'
MAIN_LOGGER = "eyed3"

# Add some levels
logging.VERBOSE = logging.DEBUG + 1
logging.addLevelName(logging.VERBOSE, "VERBOSE")

class Logger(logging.Logger):
    '''Base class for all loggers'''

    def __init__(self, name):
        logging.Logger.__init__(self, name)

        # Using propogation of child to parent, by default
        self.propagate = True
        self.setLevel(logging.NOTSET)

    def verbose(self, msg, *args, **kwargs):
        '''Log \a msg at 'verbose' level, debug < verbose < info'''
        self.log(logging.VERBOSE, msg, *args, **kwargs)


def getLogger(name):
    og_class = logging.getLoggerClass()
    try:
        logging.setLoggerClass(Logger)
        return logging.getLogger(name)
    finally:
        logging.setLoggerClass(og_class)

## The main 'eyed3' logger
log = getLogger(MAIN_LOGGER)


def initLogging():
    '''initialize the default logger with console output'''
    global log

    # Don't propgate base 'eyed3'
    log.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
    log.addHandler(console_handler)

    log.setLevel(logging.WARNING)

    return log



LEVELS = (logging.DEBUG, logging.VERBOSE, logging.INFO,
          logging.WARNING, logging.ERROR, logging.CRITICAL)
