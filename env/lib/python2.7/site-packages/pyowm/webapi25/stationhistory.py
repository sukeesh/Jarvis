"""
Module containing classes and datastructures related to meteostation history
data
"""

import json
import xml.etree.ElementTree as ET
from pyowm.webapi25.xsd.xmlnsconfig import (
    STATION_HISTORY_XMLNS_PREFIX, STATION_HISTORY_XMLNS_URL)
from pyowm.utils import timeformatutils, xmlutils


class StationHistory(object):

    """
    A class representing historic weather measurements collected by a
    meteostation. Three types of historic meteostation data can be obtained by
    the OWM web API: ticks (one data chunk per minute) data, hourly and daily
    data.

    :param station_ID: the numeric ID of the meteostation
    :type station_ID: int
    :param interval: the time granularity of the meteostation data history
    :type interval: str
    :param reception_time: GMT UNIXtime of the data reception from the OWM web
         API
    :type reception_time: int
    :param measurements: a dictionary containing raw weather measurements
    :type measurements: dict
    :returns: a *StationHistory* instance
    :raises: *ValueError* when the supplied value for reception time is
        negative
    """

    def __init__(self, station_ID, interval, reception_time, measurements):
        self._station_ID = station_ID
        self._interval = interval
        if reception_time < 0:
            raise ValueError("'reception_time' must be greater than 0")
        self._reception_time = reception_time
        self._measurements = measurements

    def get_station_ID(self):
        """
        Returns the ID of the meteostation

        :returns: the int station ID

        """
        return self._station_ID

    def set_station_ID(self, station_ID):
        """
        Sets the numeric ID of the meteostation

        :param station_ID: the numeric ID of the meteostation
        :type station_ID: int

        """
        self._station_ID = station_ID

    def get_interval(self):
        """
        Returns the interval of the meteostation history data

        :returns: the int interval

        """
        return self._interval

    def set_interval(self, interval):
        """
        Sets the interval of the meteostation history data

        :param interval: the time granularity of the meteostation history data,
            may be among "tick","hour" and "day"
        :type interval: string

        """
        self._interval = interval

    def get_measurements(self):
        """
        Returns the measurements of the meteostation as a dict. The dictionary
        keys are UNIX timestamps and for each one the value is a dict
        containing the keys 'temperature','humidity','pressure','rain','wind'
        along with their corresponding numeric values.
        Eg: ``{1362933983: { "temperature": 266.25, "humidity": 27.3,
        "pressure": 1010.02, "rain": None, "wind": 4.7}, ... }``

        :returns: the dict containing the meteostation's measurements

        """
        return self._measurements

    def get_reception_time(self, timeformat='unix'):
        """Returns the GMT time telling when the meteostation history data was
           received from the OWM web API

        :param timeformat: the format for the time value. May be:
            '*unix*' (default) for UNIX time
            '*iso*' for ISO8601-formatted string in the format ``YYYY-MM-DD HH:MM:SS+00``
            '*date* for ``datetime.datetime`` object instance
        :type timeformat: str
        :returns: an int or a str
        :raises: ValueError

        """
        return timeformatutils.timeformat(self._reception_time, timeformat)

    def to_JSON(self):
        """Dumps object fields into a JSON formatted string

        :returns: the JSON string

        """
        return json.dumps({"station_ID": self._station_ID,
                            "interval": self._interval,
                            "reception_time": self._reception_time,
                            "measurements": self._measurements
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
                                         STATION_HISTORY_XMLNS_PREFIX,
                                         STATION_HISTORY_XMLNS_URL)
        return xmlutils.DOM_node_to_XML(root_node, xml_declaration)

    def _to_DOM(self):
        """
        Dumps object data to a fully traversable DOM representation of the
        object.

        :returns: a ``xml.etree.Element`` object

        """
        root_node = ET.Element("station_history")
        station_id_node = ET.SubElement(root_node, "station_id")
        station_id_node.text = str(self._station_ID)
        interval_node = ET.SubElement(root_node, "interval")
        interval_node.text = self._interval
        reception_time_node = ET.SubElement(root_node, "reception_time")
        reception_time_node.text = str(self._reception_time)
        measurements_node = ET.SubElement(root_node, "measurements")
        for m in self._measurements:
            d = self._measurements[m].copy()
            d['reference_time'] = m
            xmlutils.create_DOM_node_from_dict(d, "measurement",
                                               measurements_node)
        return root_node

    def __len__(self):
        return len(self._measurements)

    def __repr__(self):
        return '<%s.%s - station ID=%s, reception time=%s, interval=%s, ' \
               'measurements:%s>' % (__name__, self.__class__.__name__,
                                     self._station_ID,
                                     self.get_reception_time('iso'),
                                     self._interval, str(len(self))
                                     )
