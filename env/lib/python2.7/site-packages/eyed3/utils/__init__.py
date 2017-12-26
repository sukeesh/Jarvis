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
from __future__ import print_function
import os
import re
import math
import logging
import argparse
import warnings
import threading
from ..compat import unicode, StringIO, PY2

ID3_MIME_TYPE = "application/x-id3"
ID3_MIME_TYPE_EXTENSIONS = (".id3", ".tag")

import mimetypes
_mime_types = mimetypes.MimeTypes()
_mime_types.readfp(StringIO("%s %s" %
                   (ID3_MIME_TYPE,
                    " ".join((e[1:] for e in ID3_MIME_TYPE_EXTENSIONS)))))
del mimetypes
del StringIO

from eyed3 import LOCAL_ENCODING, LOCAL_FS_ENCODING

from ..utils.log import getLogger
log = getLogger(__name__)


def guessMimetype(filename, with_encoding=False):
    '''Return the mime-type for ``filename``. If ``with_encoding`` is True
    the encoding is included and a 2-tuple is returned, (mine, enc).'''

    mime, enc = _mime_types.guess_type(filename, strict=False)
    return mime if not with_encoding else (mime, enc)


def walk(handler, path, excludes=None, fs_encoding=LOCAL_FS_ENCODING):
    '''A wrapper around os.walk which handles exclusion patterns and unicode
    conversion.'''
    path = unicode(path, fs_encoding) if type(path) is not unicode else path

    excludes = excludes if excludes else []
    excludes_re = []
    for e in excludes:
        excludes_re.append(re.compile(e))

    def _isExcluded(_p):
        for ex in excludes_re:
            match = ex.match(_p)
            if match:
                return True
        return False

    if not os.path.exists(path):
        raise IOError("file not found: %s" % path)
    elif os.path.isfile(path) and not _isExcluded(path):
        # If not given a directory, invoke the handler and return
        handler.handleFile(os.path.abspath(path))
        return

    for (root, dirs, files) in os.walk(path):
        root = root if type(root) is unicode else unicode(root, fs_encoding)
        dirs.sort()
        files.sort()
        for f in files:
            f = f if type(f) is unicode else unicode(f, fs_encoding)
            f = os.path.abspath(os.path.join(root, f))
            if not _isExcluded(f):
                try:
                    handler.handleFile(f)
                except StopIteration:
                    return

        if files:
            handler.handleDirectory(root, files)


class FileHandler(object):
    '''A handler interface for :func:`eyed3.utils.walk` callbacks.'''

    def handleFile(self, f):
        '''Called for each file walked. The file ``f`` is the full path and
        the return value is ignored. If the walk should abort the method should
        raise a ``StopIteration`` exception.'''
        pass

    def handleDirectory(self, d, files):
        '''Called for each directory ``d`` **after** ``handleFile`` has been
        called for each file in ``files``. ``StopIteration`` may be raised to
        halt iteration.'''
        pass

    def handleDone(self):
        '''Called when there are no more files to handle.'''
        pass


def requireUnicode(*args):
    '''Function decorator to enforce unicode argument types.
    ``None`` is a valid argument value, in all cases, regardless of not being
    unicode.  ``*args`` Positional arguments may be numeric argument index
    values (requireUnicode(1, 3) - requires argument 1 and 3 are unicode)
    or keyword argument names (requireUnicode("title")) or a combination
    thereof.
    '''
    arg_indices = []
    kwarg_names = []
    for a in args:
        if type(a) is int:
            arg_indices.append(a)
        else:
            kwarg_names.append(a)
    assert(arg_indices or kwarg_names)

    def wrapper(fn):
        def wrapped_fn(*args, **kwargs):
            for i in arg_indices:
                if i >= len(args):
                    # The ith argument is not there, as in optional arguments
                    break
                if args[i] is not None and not isinstance(args[i], unicode):
                    raise TypeError("%s(argument %d) must be unicode" %
                                    (fn.__name__, i))
            for name in kwarg_names:
                if (name in kwargs and kwargs[name] is not None and
                        not isinstance(kwargs[name], unicode)):
                    raise TypeError("%s(argument %s) must be unicode" %
                                    (fn.__name__, name))
            return fn(*args, **kwargs)
        return wrapped_fn
    return wrapper


def encodeUnicode(replace=True):
    warnings.warn("use compat PY2 and be more python3", DeprecationWarning,
                  stacklevel=2)
    enc_err = "replace" if replace else "strict"

    if PY2:
        def wrapper(fn):
            def wrapped_fn(*args, **kwargs):
                new_args = []
                for a in args:
                    if type(a) is unicode:
                        new_args.append(a.encode(LOCAL_ENCODING, enc_err))
                    else:
                        new_args.append(a)
                args = tuple(new_args)

                for kw in kwargs:
                    if type(kwargs[kw]) is unicode:
                        kwargs[kw] = kwargs[kw].encode(LOCAL_ENCODING, enc_err)
                return fn(*args, **kwargs)
            return wrapped_fn
        return wrapper
    else:
        # This decorator is used to encode unicode to bytes for sys.std*
        # write calls. In python3 unicode (or str) is required by these
        # functions, the encodig happens internally.. So return a noop
        def noop(fn):
            def call(*args, **kwargs):
                return fn(*args, **kwargs)
            return noop

def formatTime(seconds, total=None, short=False):
    '''
    Format ``seconds`` (number of seconds) as a string representation.
    When ``short`` is False (the default) the format is:

        HH:MM:SS.

    Otherwise, the format is exacly 6 characters long and of the form:

        1w 3d
        2d 4h
        1h 5m
        1m 4s
        15s

    If ``total`` is not None it will also be formatted and
    appended to the result seperated by ' / '.
    '''
    def time_tuple(ts):
        if ts is None or ts < 0:
            ts = 0
        hours = ts / 3600
        mins = (ts % 3600) / 60
        secs = (ts % 3600) % 60
        tstr = '%02d:%02d' % (mins, secs)
        if int(hours):
            tstr = '%02d:%s' % (hours, tstr)
        return (int(hours), int(mins), int(secs), tstr)

    if not short:
        hours, mins, secs, curr_str = time_tuple(seconds)
        retval = curr_str
        if total:
            hours, mins, secs, total_str = time_tuple(total)
            retval += ' / %s' % total_str
        return retval
    else:
        units = [
            (u'y', 60 * 60 * 24 * 7 * 52),
            (u'w', 60 * 60 * 24 * 7),
            (u'd', 60 * 60 * 24),
            (u'h', 60 * 60),
            (u'm', 60),
            (u's', 1),
        ]

        seconds = int(seconds)

        if seconds < 60:
            return u'   {0:02d}s'.format(seconds)
        for i in xrange(len(units) - 1):
            unit1, limit1 = units[i]
            unit2, limit2 = units[i + 1]
            if seconds >= limit1:
                return u'{0:02d}{1}{2:02d}{3}'.format(
                    seconds // limit1, unit1,
                    (seconds % limit1) // limit2, unit2)
        return u'  ~inf'


KB_BYTES = 1024
'''Number of bytes per KB (2^10)'''
MB_BYTES = 1048576
'''Number of bytes per MB (2^20)'''
GB_BYTES = 1073741824
'''Number of bytes per GB (2^30)'''
KB_UNIT = "KB"
'''Kilobytes abbreviation'''
MB_UNIT = "MB"
'''Megabytes abbreviation'''
GB_UNIT = "GB"
'''Gigabytes abbreviation'''


def formatSize(size, short=False):
    '''Format ``size`` (nuber of bytes) into string format doing KB, MB, or GB
    conversion where necessary.

    When ``short`` is False (the default) the format is smallest unit of
    bytes and largest gigabytes; '234 GB'.
    The short version is 2-4 characters long and of the form

        256b
        64k
        1.1G
    '''
    if not short:
        unit = "Bytes"
        if size >= GB_BYTES:
            size = float(size) / float(GB_BYTES)
            unit = GB_UNIT
        elif size >= MB_BYTES:
            size = float(size) / float(MB_BYTES)
            unit = MB_UNIT
        elif size >= KB_BYTES:
            size = float(size) / float(KB_BYTES)
            unit = KB_UNIT
        return "%.2f %s" % (size, unit)
    else:
        suffixes = u' kMGTPEH'
        if size == 0:
            num_scale = 0
        else:
            num_scale = int(math.floor(math.log(size) / math.log(1000)))
        if num_scale > 7:
            suffix = '?'
        else:
            suffix = suffixes[num_scale]
        num_scale = int(math.pow(1000, num_scale))
        value = size / num_scale
        str_value = str(value)
        if len(str_value) >= 3 and str_value[2] == '.':
            str_value = str_value[:2]
        else:
            str_value = str_value[:3]
        return "{0:>3s}{1}".format(str_value, suffix)


def formatTimeDelta(td):
    '''Format a timedelta object ``td`` into a string. '''
    days = td.days
    hours = td.seconds / 3600
    mins = (td.seconds % 3600) / 60
    secs = (td.seconds % 3600) % 60
    tstr = "%02d:%02d:%02d" % (hours, mins, secs)
    if days:
        tstr = "%d days %s" % (days, tstr)
    return tstr


def chunkCopy(src_fp, dest_fp, chunk_sz=(1024 * 512)):
    '''Copy ``src_fp`` to ``dest_fp`` in ``chunk_sz`` byte increments.'''
    done = False
    while not done:
        data = src_fp.read(chunk_sz)
        if data:
            dest_fp.write(data)
        else:
            done = True
        del data


class ArgumentParser(argparse.ArgumentParser):
    '''Subclass of argparse.ArgumentParser that adds version and log level
    options.'''

    def __init__(self, *args, **kwargs):
        from eyed3.info import VERSION
        from eyed3.utils.log import LEVELS
        from eyed3.utils.log import MAIN_LOGGER

        def pop_kwarg(name, default):
            if name in kwargs:
                value = kwargs.pop(name) or default
            else:
                value = default
            return value
        main_logger = pop_kwarg("main_logger", MAIN_LOGGER)
        version = pop_kwarg("version", VERSION)

        self.log_levels = [logging.getLevelName(l).lower() for l in LEVELS]

        formatter = argparse.RawDescriptionHelpFormatter
        super(ArgumentParser, self).__init__(*args, formatter_class=formatter,
                                             **kwargs)

        self.add_argument("--version", action="version", version=version,
                          help="Display version information and exit")

        self.debug_arg_group = self.add_argument_group("Debugging")
        self.debug_arg_group.add_argument(
                "-l", "--log-level", metavar="LEVEL[:LOGGER]",
                action=LoggingAction, main_logger=main_logger,
                help="Set a log level. This option may be specified multiple "
                     "times. If a logger name is specified than the level "
                     "applies only to that logger, otherwise the level is set "
                     "on the top-level logger. Acceptable levels are %s. " %
                     (", ".join("'%s'" % l for l in self.log_levels)))


class LoggingAction(argparse._AppendAction):
    def __init__(self, *args, **kwargs):
        self.main_logger = kwargs.pop("main_logger")
        super(LoggingAction, self).__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):

        values = values.split(':')
        level, logger = values if len(values) > 1 else (values[0],
                                                        self.main_logger)

        logger = logging.getLogger(logger)
        try:
            logger.setLevel(logging._levelNames[level.upper()])
        except KeyError:
            msg = "invalid level choice: %s (choose from %s)" % \
                   (level, parser.log_levels)
            raise argparse.ArgumentError(self, msg)

        super(LoggingAction, self).__call__(parser, namespace, values,
                                            option_string)


def datePicker(thing, prefer_recording_date=False):
    '''This function returns a date of some sort, amongst all the possible
    dates (members called release_date, original_release_date,
    and recording_date of type eyed3.core.Date).

    The order of preference is:
    1) date of original release
    2) date of this versions release
    3) the recording date.

    Unless ``prefer_recording_date`` is ``True`` in which case the order is
    3, 1, 2.

    ``None`` will be returned if no dates are available.'''
    if not prefer_recording_date:
        return (thing.original_release_date or
                thing.release_date or
                thing.recording_date)
    else:
        return (thing.recording_date or
                thing.original_release_date or
                thing.release_date)


def makeUniqueFileName(file_path, uniq=u''):
    '''The ``file_path`` is the desired file name, and it is returned if the
    file does not exist. In the case that it already exists the path is
    adjusted to be unique. First, the ``uniq`` string is added, and then
    a couter is used to find a unique name.'''

    path = os.path.dirname(file_path)
    file = os.path.basename(file_path)
    name, ext = os.path.splitext(file)
    count = 1
    while os.path.exists(os.path.join(path, file)):
        if uniq:
            name = "%s_%s" % (name, uniq)
            file = "".join([name, ext])
            uniq = u''
        else:
            file = "".join(["%s_%s" % (name, count), ext])
            count += 1
    return os.path.join(path, file)
