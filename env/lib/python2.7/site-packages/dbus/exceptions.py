"""D-Bus exceptions."""

# Copyright (C) 2007 Collabora Ltd. <http://www.collabora.co.uk/>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

__all__ = ('DBusException', 'MissingErrorHandlerException',
           'MissingReplyHandlerException', 'ValidationException',
           'IntrospectionParserException', 'UnknownMethodException',
           'NameExistsException')

from dbus._compat import is_py3


class DBusException(Exception):

    include_traceback = False
    """If True, tracebacks will be included in the exception message sent to
    D-Bus clients.

    Exceptions that are not DBusException subclasses always behave
    as though this is True. Set this to True on DBusException subclasses
    that represent a programming error, and leave it False on subclasses that
    represent an expected failure condition (e.g. a network server not
    responding)."""

    def __init__(self, *args, **kwargs):
        name = kwargs.pop('name', None)
        if name is not None or getattr(self, '_dbus_error_name', None) is None:
            self._dbus_error_name = name
        if kwargs:
            raise TypeError('DBusException does not take keyword arguments: %s'
                            % ', '.join(kwargs.keys()))
        Exception.__init__(self, *args)

    def __unicode__(self):
        """Return a unicode error"""
        # We can't just use Exception.__unicode__ because it chains up weirdly.
        # https://code.launchpad.net/~mvo/ubuntu/quantal/dbus-python/lp846044/+merge/129214
        if len(self.args) > 1:
            s = unicode(self.args)
        else:
            s = ''.join(self.args)

        if self._dbus_error_name is not None:
            return '%s: %s' % (self._dbus_error_name, s)
        else:
            return s

    def __str__(self):
        """Return a str error"""
        s = Exception.__str__(self)
        if self._dbus_error_name is not None:
            return '%s: %s' % (self._dbus_error_name, s)
        else:
            return s

    def get_dbus_message(self):
        if len(self.args) > 1:
            if is_py3:
                s = str(self.args)
            else:
                s = unicode(self.args)
        else:
            s = ''.join(self.args)

        if isinstance(s, bytes):
            return s.decode('utf-8', 'replace')

        return s

    def get_dbus_name(self):
        return self._dbus_error_name

class MissingErrorHandlerException(DBusException):

    include_traceback = True

    def __init__(self):
        DBusException.__init__(self, "error_handler not defined: if you define a reply_handler you must also define an error_handler")

class MissingReplyHandlerException(DBusException):

    include_traceback = True

    def __init__(self):
        DBusException.__init__(self, "reply_handler not defined: if you define an error_handler you must also define a reply_handler")

class ValidationException(DBusException):

    include_traceback = True

    def __init__(self, msg=''):
        DBusException.__init__(self, "Error validating string: %s"%msg)

class IntrospectionParserException(DBusException):

    include_traceback = True

    def __init__(self, msg=''):
        DBusException.__init__(self, "Error parsing introspect data: %s"%msg)

class UnknownMethodException(DBusException):

    include_traceback = True
    _dbus_error_name = 'org.freedesktop.DBus.Error.UnknownMethod'

    def __init__(self, method):
        DBusException.__init__(self, "Unknown method: %s"%method)

class NameExistsException(DBusException):

    include_traceback = True

    def __init__(self, name):
        DBusException.__init__(self, "Bus name already exists: %s"%name)
