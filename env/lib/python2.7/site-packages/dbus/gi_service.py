"""Support code for implementing D-Bus services via PyGI."""

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

__all__ = ['ExportedGObject']

from gi.repository import GObject
import dbus.service

# The odd syntax used here is required so that the code is compatible with
# both Python 2 and Python 3.  It essentially creates a new class called
# ExportedGObject with a metaclass of ExportGObjectType and an __init__()
# function.
#
# Because GObject and `dbus.service.Object` both have custom metaclasses, the
# naive approach using simple multiple inheritance won't work. This class has
# `ExportedGObjectType` as its metaclass, which is sufficient to make it work
# correctly.

class ExportedGObjectType(GObject.GObject.__class__, dbus.service.InterfaceType):
    """A metaclass which inherits from both GObjectMeta and
    `dbus.service.InterfaceType`. Used as the metaclass for `ExportedGObject`.
    """
    def __init__(cls, name, bases, dct):
        GObject.GObject.__class__.__init__(cls, name, bases, dct)
        dbus.service.InterfaceType.__init__(cls, name, bases, dct)


def ExportedGObject__init__(self, conn=None, object_path=None, **kwargs):
    """Initialize an exported GObject.

    :Parameters:
        `conn` : dbus.connection.Connection
            The D-Bus connection or bus
        `object_path` : str
            The object path at which to register this object.
    :Keywords:
        `bus_name` : dbus.service.BusName
            A bus name to be held on behalf of this object, or None.
        `gobject_properties` : dict
            GObject properties to be set on the constructed object.

            Any unrecognised keyword arguments will also be interpreted
            as GObject properties.
        """
    bus_name = kwargs.pop('bus_name', None)
    gobject_properties = kwargs.pop('gobject_properties', None)

    if gobject_properties is not None:
        kwargs.update(gobject_properties)
    GObject.GObject.__init__(self, **kwargs)
    dbus.service.Object.__init__(self, conn=conn,
                                 object_path=object_path,
                                 bus_name=bus_name)

ExportedGObject__doc__ = 'A GObject which is exported on the D-Bus.'

ExportedGObject = ExportedGObjectType(
    'ExportedGObject',
    (GObject.GObject, dbus.service.Object),
    {'__init__': ExportedGObject__init__,
     '__doc__': ExportedGObject__doc__,
     })
