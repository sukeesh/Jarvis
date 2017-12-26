"""
Module containing weather forecast classes and data structures.
"""

import json
import xml.etree.ElementTree as ET
from pyowm.webapi25.xsd.xmlnsconfig import (
    FORECAST_XMLNS_PREFIX, FORECAST_XMLNS_URL)
from pyowm.utils import timeformatutils, xmlutils


class ForecastIterator(object):
    """
    Iterator over the list of *Weather* objects encapsulated in a *Forecast*
    class instance

    :param obj: the iterable object
    :type obj: object
    :returns:  a *ForecastIterator* instance

    """
    def __init__(self, obj):
        self._obj = obj
        self._cnt = 0

    def next(self):
        """
        Compatibility for Python 2.x, delegates to function: `__next__()`
        Returns the next *Weather* item

        :returns: the next *Weather* item

        """
        return self.__next__()

    def __next__(self):
        """
        Returns the next *Weather* item

        :returns: the next *Weather* item

        """
        try:
            result = self._obj.get(self._cnt)
            self._cnt += 1
            return result
        except IndexError:
            raise StopIteration


class Forecast(object):
    """
    A class encapsulating weather forecast data for a certain location and
    relative to a specific time interval (forecast for every three hours or
    for every day)

    :param interval: the time granularity of the forecast. May be: *'3h'* for
        three hours forecast or *'daily'* for daily ones
    :type interval: str
    :param reception_time: GMT UNIXtime of the forecast reception from the OWM
        web API
    :type reception_time: int
    :param location: the *Location* object relative to the forecast
    :type location: Location
    :param weathers: the list of *Weather* objects composing the forecast
    :type weathers: list
    :returns:  a *Forecast* instance
    :raises: *ValueError* when negative values are provided

    """

    def __init__(self, interval, reception_time, location, weathers):
        self._interval = interval
        if reception_time < 0:
            raise ValueError("'reception_time' must be greater than 0")
        self._reception_time = reception_time
        self._location = location
        self._weathers = weathers

    def __iter__(self):
        """
        Creates a *ForecastIterator* instance

        :returns: a *ForecastIterator* instance
        """
        return ForecastIterator(self)

    def get(self, index):
        """
        Lookups up into the *Weather* items list for the item at the specified
        index

        :param index: the index of the *Weather* object in the list
        :type index: int
        :returns: a *Weather* object
        """
        return self._weathers[index]

    def get_interval(self):
        """
        Returns the time granularity of the forecast

        :returns: str

        """
        return self._interval

    def set_interval(self, interval):
        """
        Sets the time granularity of the forecast

        :param interval: the time granularity of the forecast, may be "3h" or
            "daily"
        :type interval: str

        """
        self._interval = interval

    def get_reception_time(self, timeformat='unix'):
        """Returns the GMT time telling when the forecast was received
            from the OWM web API

        :param timeformat: the format for the time value. May be:
            '*unix*' (default) for UNIX time
            '*iso*' for ISO8601-formatted string in the format ``YYYY-MM-DD HH:MM:SS+00``
            '*date* for ``datetime.datetime`` object instance
        :type timeformat: str
        :returns: an int or a str
        :raises: ValueError

        """
        return timeformatutils.timeformat(self._reception_time, timeformat)

    def get_location(self):
        """
        Returns the Location object relative to the forecast

        :returns: a *Location* object

        """
        return self._location

    def get_weathers(self):
        """
        Returns a copy of the *Weather* objects list composing the forecast

        :returns: a list of *Weather* objects

        """
        return list(self._weathers)

    def count_weathers(self):
        """
        Tells how many *Weather* items compose the forecast

        :returns: the *Weather* objects total

        """
        return len(self._weathers)

    def to_JSON(self):
        """Dumps object fields into a JSON formatted string

        :returns: the JSON string

        """
        return json.dumps({"interval": self._interval,
                           "reception_time": self._reception_time,
                           "Location": json.loads(self._location.to_JSON()),
                           "weathers": json.loads("[" + \
                                ",".join([w.to_JSON() for w in self]) + "]")
                           })

    def to_XML(self, xml_declaration=True, xmlns=True):
        """
        Dumps object fields to an XML-formatted string. The 'xml_declaration'
        switch  enables printing of a leading standard XML line containing XML
        version and encoding. The 'xmlns' switch enables printing of qualified
        XMLNS prefixes.

        :param XML_declaration: if ``True`` (default) prints a leading XML
            declaration line
        :type XML_declaration: bool
        :param xmlns: if ``True`` (default) prints full XMLNS prefixes
        :type xmlns: bool
        :returns: an XML-formatted string

        """
        root_node = self._to_DOM()
        if xmlns:
            xmlutils.annotate_with_XMLNS(root_node,
                                         FORECAST_XMLNS_PREFIX,
                                         FORECAST_XMLNS_URL)
        return xmlutils.DOM_node_to_XML(root_node, xml_declaration)

    def _to_DOM(self):
        """
        Dumps object data to a fully traversable DOM representation of the
        object.

        :returns: a ``xml.etree.Element`` object

        """
        root_node = ET.Element("forecast")
        interval_node = ET.SubElement(root_node, "interval")
        interval_node.text = self._interval
        reception_time_node = ET.SubElement(root_node, "reception_time")
        reception_time_node.text = str(self._reception_time)
        root_node.append(self._location._to_DOM())
        weathers_node = ET.SubElement(root_node, "weathers")
        for weather in self:
            weathers_node.append(weather._to_DOM())
        return root_node

    def __len__(self):
        """Redefine __len__ hook"""
        return self.count_weathers()

    def __repr__(self):
        return "<%s.%s - reception time=%s, interval=%s>" % (__name__, \
              self.__class__.__name__, self.get_reception_time('iso'),
              self._interval)
