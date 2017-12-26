"""
Carbon Monoxide classes and data structures.
"""

import json
import xml.etree.ElementTree as ET
from pyowm.webapi25.xsd.xmlnsconfig import (
    COINDEX_XMLNS_URL, COINDEX_XMLNS_PREFIX)
from pyowm.utils import timeformatutils, timeutils, xmlutils


class COIndex(object):
    """
    A class representing the Carbon monOxide Index observed in a certain location
    in the world. The index is made up of several measurements, each one at a
    different atmospheric pressure. The location is represented by the
    encapsulated *Location* object.

    :param reference_time: GMT UNIXtime telling when the CO data has been measured
    :type reference_time: int
    :param location: the *Location* relative to this CO observation
    :type location: *Location*
    :param interval: the time granularity of the CO observation
    :type interval: str
    :param co_samples: the CO samples
    :type co_samples: list of dicts
    :param reception_time: GMT UNIXtime telling when the CO observation has
        been received from the OWM web API
    :type reception_time: int
    :returns: an *COIndex* instance
    :raises: *ValueError* when negative values are provided as reception time,
      CO samples are not provided in a list

    """

    def __init__(self, reference_time, location, interval, co_samples,
                 reception_time):
        if reference_time < 0:
            raise ValueError("'reference_time' must be greater than 0")
        self._reference_time = reference_time
        self._location = location
        self._interval = interval
        if not isinstance(co_samples, list):
            raise ValueError("'co_samples' must be a list")
        self._co_samples = sorted(co_samples, key=lambda k: k['value'], reverse=True)
        if reception_time < 0:
            raise ValueError("'reception_time' must be greater than 0")
        self._reception_time = reception_time

    def get_reference_time(self, timeformat='unix'):
        """
        Returns the GMT time telling when the CO samples have been measured

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
        Returns the GMT time telling when the CO observation has been received
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
        Returns the *Location* object for this CO index measurement

        :returns: the *Location* object

        """
        return self._location

    def get_interval(self):
        """
        Returns the time granularity interval for this CO index measurement

        :return: str
        """
        return self._interval

    def get_co_samples(self):
        """
        Returns the CO samples for this index

        :returns: list of dicts

        """
        return self._co_samples

    def get_co_sample_with_highest_vmr(self):
        """
        Returns the CO sample with the highest Volume Mixing Ratio value
        :return: dict
        """
        return max(self._co_samples, key=lambda x: x['value'])

    def get_co_sample_with_lowest_vmr(self):
        """
        Returns the CO sample with the lowest Volume Mixing Ratio value
        :return: dict
        """
        return min(self._co_samples, key=lambda x: x['value'])

    def is_forecast(self):
        """
        Tells if the current CO observation refers to the future with respect
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
                           "co_samples": self._co_samples,
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
                                         COINDEX_XMLNS_PREFIX,
                                         COINDEX_XMLNS_URL)
        return xmlutils.DOM_node_to_XML(root_node, xml_declaration)

    def _to_DOM(self):
        """
        Dumps object data to a fully traversable DOM representation of the
        object.

        :returns: a ``xml.etree.Element`` object

        """
        root_node = ET.Element("coindex")
        reference_time_node = ET.SubElement(root_node, "reference_time")
        reference_time_node.text = str(self._reference_time)
        reception_time_node = ET.SubElement(root_node, "reception_time")
        reception_time_node.text = str(self._reception_time)
        interval_node = ET.SubElement(root_node, "interval")
        interval_node.text = str(self._interval)
        co_samples_node = ET.SubElement(root_node, "co_samples")
        for smpl in self._co_samples:
            s = smpl.copy()
            # turn values to 12 decimal digits-formatted strings
            s['pressure'] = '{:.12e}'.format(s['pressure'])
            s['value'] = '{:.12e}'.format(s['value'])
            s['precision'] = '{:.12e}'.format(s['precision'])
            xmlutils.create_DOM_node_from_dict(s, "co_sample",
                                               co_samples_node)
        root_node.append(self._location._to_DOM())
        return root_node

    def __repr__(self):
        return "<%s.%s - reference time=%s, reception time=%s, location=%s, " \
               "interval=%s>" % (
                    __name__,
                    self.__class__.__name__,
                    self.get_reference_time('iso'),
                    self.get_reception_time('iso'),
                    str(self._location),
                    self._interval)
