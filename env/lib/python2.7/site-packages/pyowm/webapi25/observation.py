"""
Weather observation classes and data structures.
"""

import json
import xml.etree.ElementTree as ET
from pyowm.webapi25.xsd.xmlnsconfig import (
    OBSERVATION_XMLNS_URL, OBSERVATION_XMLNS_PREFIX)
from pyowm.utils import timeformatutils, xmlutils


class Observation(object):
    """
    A class representing the weather which is currently being observed in a
    certain location in the world. The location is represented by the
    encapsulated *Location* object while the observed weather data are held by
    the encapsulated *Weather* object.

    :param reception_time: GMT UNIXtime telling when the weather obervation has
        been received from the OWM web API
    :type reception_time: int
    :param location: the *Location* relative to this observation
    :type location: *Location*
    :param weather: the *Weather* relative to this observation
    :type weather: *Weather*
    :returns: an *Observation* instance
    :raises: *ValueError* when negative values are provided as reception time

    """

    def __init__(self, reception_time, location, weather):
        if reception_time < 0:
            raise ValueError("'reception_time' must be greater than 0")
        self._reception_time = reception_time
        self._location = location
        self._weather = weather

    def get_reception_time(self, timeformat='unix'):
        """
        Returns the GMT time telling when the observation has been received
          from the OWM web API

        :param timeformat: the format for the time value. May be:
            '*unix*' (default) for UNIX time
            '*iso*' for ISO8601-formatted string in the format ``YYYY-MM-DD HH:MM:SS+00``
            '*date* for ``datetime.datetime`` object instance
        :type timeformat: str
        :returns: an int or a str
        :raises: ValueError when negative values are provided

        """
        return timeformatutils.timeformat(self._reception_time, timeformat)

    def get_location(self):
        """
        Returns the *Location* object for this observation

        :returns: the *Location* object

        """
        return self._location

    def get_weather(self):
        """
        Returns the *Weather* object for this observation

        :returns: the *Weather* object

        """
        return self._weather

    def to_JSON(self):
        """Dumps object fields into a JSON formatted string

        :returns:  the JSON string

        """
        return json.dumps({"reception_time": self._reception_time,
                           "Location": json.loads(self._location.to_JSON()),
                           "Weather": json.loads(self._weather.to_JSON())
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
                                         OBSERVATION_XMLNS_PREFIX,
                                         OBSERVATION_XMLNS_URL)
        return xmlutils.DOM_node_to_XML(root_node, xml_declaration)

    def _to_DOM(self):
        """
        Dumps object data to a fully traversable DOM representation of the
        object.

        :returns: a ``xml.etree.Element`` object

        """
        root_node = ET.Element("observation")
        reception_time_node = ET.SubElement(root_node, "reception_time")
        reception_time_node.text = str(self._reception_time)
        root_node.append(self._location._to_DOM())
        root_node.append(self._weather._to_DOM())
        return root_node

    def __repr__(self):
        return "<%s.%s - reception time=%s>" % (__name__, \
              self.__class__.__name__, self.get_reception_time('iso'))
