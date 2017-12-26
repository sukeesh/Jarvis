# Copyright (C) 2006 Collabora Ltd. <http://www.collabora.co.uk/>
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

"""Low-level interface to D-Bus."""

__all__ = ('PendingCall', 'Message', 'MethodCallMessage',
           'MethodReturnMessage', 'ErrorMessage', 'SignalMessage',
           'HANDLER_RESULT_HANDLED', 'HANDLER_RESULT_NOT_YET_HANDLED',
           'MESSAGE_TYPE_INVALID', 'MESSAGE_TYPE_METHOD_CALL',
           'MESSAGE_TYPE_METHOD_RETURN', 'MESSAGE_TYPE_ERROR',
           'MESSAGE_TYPE_SIGNAL')

from _dbus_bindings import (
    ErrorMessage, HANDLER_RESULT_HANDLED, HANDLER_RESULT_NOT_YET_HANDLED,
    MESSAGE_TYPE_ERROR, MESSAGE_TYPE_INVALID, MESSAGE_TYPE_METHOD_CALL,
    MESSAGE_TYPE_METHOD_RETURN, MESSAGE_TYPE_SIGNAL, Message,
    MethodCallMessage, MethodReturnMessage, PendingCall, SignalMessage)
