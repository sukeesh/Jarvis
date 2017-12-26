# Copyright (C) 2003, 2004, 2005, 2006 Red Hat Inc. <http://www.redhat.com/>
# Copyright (C) 2003 David Zeuthen
# Copyright (C) 2004 Rob Taylor
# Copyright (C) 2005, 2006 Collabora Ltd. <http://www.collabora.co.uk/>
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

from xml.parsers.expat import ParserCreate
from dbus.exceptions import IntrospectionParserException

class _Parser(object):
    __slots__ = ('map', 'in_iface', 'in_method', 'sig')
    def __init__(self):
        self.map = {}
        self.in_iface = ''
        self.in_method = ''
        self.sig = ''

    def parse(self, data):
        parser = ParserCreate('UTF-8', ' ')
        parser.buffer_text = True
        parser.StartElementHandler = self.StartElementHandler
        parser.EndElementHandler = self.EndElementHandler
        parser.Parse(data)
        return self.map

    def StartElementHandler(self, name, attributes):
        if not self.in_iface:
            if (not self.in_method and name == 'interface'):
                self.in_iface = attributes['name']
        else:
            if (not self.in_method and name == 'method'):
                self.in_method = attributes['name']
            elif (self.in_method and name == 'arg'):
                if attributes.get('direction', 'in') == 'in':
                    self.sig += attributes['type']

    def EndElementHandler(self, name):
        if self.in_iface:
            if (not self.in_method and name == 'interface'):
                self.in_iface = ''
            elif (self.in_method and name == 'method'):
                self.map[self.in_iface + '.' + self.in_method] = self.sig
                self.in_method = ''
                self.sig = ''

def process_introspection_data(data):
    """Return a dict mapping ``interface.method`` strings to the
    concatenation of all their 'in' parameters, and mapping
    ``interface.signal`` strings to the concatenation of all their
    parameters.

    Example output::

        {
            'com.example.SignalEmitter.OneString': 's',
            'com.example.MethodImplementor.OneInt32Argument': 'i',
        }

    :Parameters:
        `data` : str
            The introspection XML. Must be an 8-bit string of UTF-8.
    """
    try:
        return _Parser().parse(data)
    except Exception as e:
        raise IntrospectionParserException('%s: %s' % (e.__class__, e))
