"""
Module containing classes and data structures related to meteostation data
"""

import json
import xml.etree.ElementTree as ET

from pyowm.webapi25 import weather
from pyowm.webapi25.xsd.xmlnsconfig import (
    LIST_STATION_XMLNS_PREFIX, LIST_STATION_XMLNS_URL)
from pyowm.utils import timeformatutils, xmlutils


class Station(object):
    """
    A class representing meteostations which are reporting current weather
    conditions from geographical coordinates.

    :param name: meteostation name
    :type name: string
    :param station_ID: OWM station ID
    :type station_ID: int
    :param station_type: meteostation type
    :type station_type: int
    :param status: station status
    :type status: int
    :param lat: latitude for station
    :type lat: float
    :param lon: longitude for station
    :type lon: float
    :param distance: distance of station from lat/lon of search criteria
    :type distance: float
    :param last_weather: last reported weather conditions from station
    :type last_weather: *Weather* instance
    :returns: a *Station* instance
    :raises: *ValueError* if `lon` or `lat` values are provided out of bounds or
        `last_weather` is not an instance of *Weather* or `None`

    """

    def __init__(self, name, station_ID, station_type, status, lat, lon,
                 distance=None, last_weather=None):

        if lon < -180.0 or lon > 180.0:
            raise ValueError("'lon' value must be between -180 and 180")
        if lat < -90.0 or lat > 90.0:
            raise ValueError("'lat' value must be between -90 and 90")
        if last_weather is not None:
            if not isinstance(last_weather, weather.Weather):
                raise ValueError('`last_weather` must be a Weather object')
        self._name = name
        self._station_ID = station_ID
        self._station_type = station_type
        self._status = status
        self._lat = float(lat)
        self._lon = float(lon)
        self._distance = float(distance) if distance is not None else None
        self._last_weather = last_weather

    def get_name(self):
        """
        Returns the name of the station

        :returns: the Unicode station name

        """
        return self._name

    def get_station_ID(self):
        """
        Returns the OWM station ID

        :returns: the int OWM station ID

        """
        return self._station_ID

    def get_station_type(self):
        """
        Returns the OWM station type

        :returns: the int OWM station type

        """
        return self._station_type

    def get_status(self):
        """
        Returns the OWM station status

        :returns: the int OWM station status

        """
        return self._status

    def get_lat(self):
        """
        Returns the latitude of the location

        :returns: the float latitude

        """
        return self._lat

    def get_lon(self):
        """
        Returns the longitude of the location

        :returns: the float longitude

        """
        return self._lon

    def get_distance(self):
        """
        Returns the distance of the station from the
        geo coordinates used in search

        :return: the float distance from geo coordinates

        """
        return self._distance

    def get_last_weather(self):
        """
        Returns the last reported weather conditions reported
        by the station.

        :returns: the last *Weather* instance reported by station

        """
        return self._last_weather

    def to_JSON(self):
        """Dumps object fields into a JSON formatted string

        :returns: the JSON string

        """
        last = None
        if self._last_weather:
            last = self._last_weather.to_JSON()
        return json.dumps({'name': self._name,
                           'station_ID': self._station_ID,
                           'station_type': self._station_type,
                           'status': self._status,
                           'lat': self._lat,
                           'lon': self._lon,
                           'distance': self._distance,
                           'weather': json.loads(last),
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
                                         LIST_STATION_XMLNS_PREFIX,
                                         LIST_STATION_XMLNS_URL)
        return xmlutils.DOM_node_to_XML(root_node, xml_declaration)

    def _to_DOM(self):
        """
        Dumps object data to a fully traversable DOM representation of the
        object.

        :returns: a ``xml.etree.Element`` object

        """
        last_weather = None
        if (self._last_weather
                and isinstance(self._last_weather, weather.Weather)):
            last_weather = self._last_weather._to_DOM()

        root_node = ET.Element('station')
        station_name_node = ET.SubElement(root_node, 'name')
        station_name_node.text = str(self._name)
        station_id_node = ET.SubElement(root_node, 'station_id')
        station_id_node.text = str(self._station_ID)
        station_type_node = ET.SubElement(root_node, 'station_type')
        station_type_node.text = str(self._station_type)
        status_node = ET.SubElement(root_node, 'status')
        status_node.text = str(self._status)
        coords_node = ET.SubElement(root_node, 'coords')
        lat_node = ET.SubElement(coords_node, 'lat')
        lat_node.text = str(self._lat)
        lon_node = ET.SubElement(coords_node, 'lon')
        lon_node.text = str(self._lon)
        distance_node = ET.SubElement(root_node, 'distance')
        distance_node.text = str(self._distance)
        root_node.append(last_weather)
        return root_node

    def __repr__(self):
        return '<%s.%s - station ID=%s, name=%s>' \
               % (__name__, self.__class__.__name__, self._station_ID,
                  self._name)
