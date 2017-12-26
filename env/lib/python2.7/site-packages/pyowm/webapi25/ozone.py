import json
import xml.etree.ElementTree as ET
from pyowm.webapi25.xsd.xmlnsconfig import (
    OZONE_XMLNS_URL, OZONE_XMLNS_PREFIX)
from pyowm.utils import timeformatutils, timeutils, xmlutils


class Ozone(object):
    """
    A class representing the Ozone (O3) data observed in a certain location
    in the world. The location is represented by the encapsulated *Location* object.

    :param reference_time: GMT UNIXtime telling when the O3 data have been measured
    :type reference_time: int
    :param location: the *Location* relative to this O3 observation
    :type location: *Location*
    :param du_value: the observed O3 Dobson Units value (reference:
        http://www.theozonehole.com/dobsonunit.htm)
    :type du_value: float
    :param interval: the time granularity of the O3 observation
    :type interval: str
    :param reception_time: GMT UNIXtime telling when the observation has
        been received from the OWM web API
    :type reception_time: int
    :returns: an *Ozone* instance
    :raises: *ValueError* when negative values are provided as reception time or
      du_value

    """

    def __init__(self, reference_time, location, interval, du_value, reception_time):
        if reference_time < 0:
            raise ValueError("'referencetime' must be greater than 0")
        self._reference_time = reference_time
        self._location = location
        self._interval = interval
        if du_value < 0.0:
            raise ValueError("'du_value' must be greater than 0")
        self.du_value = du_value
        if reception_time < 0:
            raise ValueError("'reception_time' must be greater than 0")
        self._reception_time = reception_time

    def get_reference_time(self, timeformat='unix'):
        """
        Returns the GMT time telling when the O3 data have been measured

        :param timeformat: the format for the time value. May be:
            '*unix*' (default) for UNIX time
            '*iso*' for ISO8601-formatted string in the format ``YYYY-MM-DD HH:MM:SS+00``
            '*date* for ``datetime.datetime`` object instance
        :type timeformat: str
        :returns: an int or a str
        :raises: ValueError when negative values are provided

        """
        return timeformatutils.timeformat(self._reference_time, timeformat)

    def get_reception_time(self, timeformat='unix'):
        """
        Returns the GMT time telling when the O3 observation
        has been received from the OWM web API

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
        Returns the *Location* object for this O3 observation

        :returns: the *Location* object

        """
        return self._location

    def get_interval(self):
        """
        Returns the time granularity interval for this O3 observation

        :return: str
        """
        return self._interval

    def get_du_value(self):
        """
        Returns the O3 Dobson Unit of this observation

        :returns: float

        """
        return self.du_value

    def is_forecast(self):
        """
        Tells if the current O3 observation refers to the future with respect
        to the current date
        :return: bool
        """
        return timeutils.now(timeformat='unix') < \
               self.get_reference_time(timeformat='unix')

    def to_JSON(self):
        """Dumps object fields into a JSON formatted string

        :returns:  the JSON string

        """
        return json.dumps({"reference_time": self._reference_time,
                           "location": json.loads(self._location.to_JSON()),
                           "interval": self._interval,
                           "value": self.du_value,
                           "reception_time": self._reception_time,
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
                                         OZONE_XMLNS_PREFIX,
                                         OZONE_XMLNS_URL)
        return xmlutils.DOM_node_to_XML(root_node, xml_declaration)

    def _to_DOM(self):
        """
        Dumps object data to a fully traversable DOM representation of the
        object.

        :returns: a ``xml.etree.Element`` object

        """
        root_node = ET.Element("ozone")
        reference_time_node = ET.SubElement(root_node, "reference_time")
        reference_time_node.text = str(self._reference_time)
        reception_time_node = ET.SubElement(root_node, "reception_time")
        reception_time_node.text = str(self._reception_time)
        interval_node = ET.SubElement(root_node, "interval")
        interval_node.text = str(self._interval)
        value_node = ET.SubElement(root_node, "value")
        value_node.text = str(self.du_value)
        root_node.append(self._location._to_DOM())
        return root_node

    def __repr__(self):
        return "<%s.%s - reference time=%s, reception time=%s, location=%s, " \
               "interval=%s, value=%s>" % (
                    __name__,
                    self.__class__.__name__,
                    self.get_reference_time('iso'),
                    self.get_reception_time('iso'),
                    str(self._location),
                    self._interval,
                    str(self.du_value))
