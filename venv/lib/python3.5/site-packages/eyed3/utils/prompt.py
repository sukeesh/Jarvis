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
import sys as _sys
from .. import LOCAL_ENCODING
from .console import Fore as fg

DISABLE_PROMPT = None
'''Whenever a prompt occurs and this value is not ``None`` it can be ``exit``
to call sys.exit (see EXIT_STATUS) or ``raise`` to throw a RunttimeError,
which can be caught if desired.'''

EXIT_STATUS = 2

BOOL_TRUE_RESPONSES = ("yes", "y", "true")


class PromptExit(RuntimeError):
    '''Raised when ``DISABLE_PROMPT`` is 'raise' and ``prompt`` is called.'''
    pass


def parseIntList(resp):
    ints = set()
    resp = resp.replace(',', ' ')
    for c in resp.split():
        i = int(c)
        ints.add(i)
    return list(ints)


def prompt(msg, default=None, required=True, type_=unicode,
           validate=None, choices=None):
    '''Prompt user for imput, the prequest is in ``msg``. If ``default`` is
    not ``None`` it will be displayed as the default and returned if not
    input is entered. The value ``None`` is only returned if ``required`` is
    ``False``. The response is passed to ``type_`` for conversion (default
    is unicode) before being returned. An optional list of valid responses can
    be provided in ``choices`.'''
    yes_no_prompt = default is True or default is False

    if yes_no_prompt:
        default_str = "Yn" if default is True else "yN"
    else:
        default_str = str(default) if default else None

    if default is not None:
        msg = "%s [%s]" % (msg, default_str)
    msg += ": " if not yes_no_prompt else "? "

    if DISABLE_PROMPT:
        if DISABLE_PROMPT == "exit":
            print(msg + "\nPrompting is disabled, exiting.")
            _sys.exit(EXIT_STATUS)
        else:
            raise PromptExit(msg)

    resp = None
    while resp is None:

        try:
            resp = raw_input(msg).decode(LOCAL_ENCODING)
        except EOFError:
            # COnverting this allows main functions to catch without
            # catching other eofs
            raise PromptExit()

        if not resp and default not in (None, ""):
            resp = str(default)

        if resp:
            if yes_no_prompt:
                resp = True if resp.lower() in BOOL_TRUE_RESPONSES else False
            else:
                resp = resp.strip()
                try:
                    resp = type_(resp)
                except Exception as ex:
                    print(fg.red(str(ex)))
                    resp = None
        elif not required:
            return None
        else:
            resp = None

        if ((choices and resp not in choices) or
                (validate and not validate(resp))):
            if choices:
                print(fg.red("Invalid response, choose from: ") + str(choices))
            else:
                print(fg.red("Invalid response"))
            resp = None

    return resp
