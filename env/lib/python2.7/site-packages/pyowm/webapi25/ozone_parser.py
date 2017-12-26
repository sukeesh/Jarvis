"""
Module containing a concrete implementation for JSONParser abstract class,
returning UVIndex objects
"""

import json
from pyowm.webapi25 import ozone
from pyowm.webapi25 import location
from pyowm.abstractions import jsonparser
from pyowm.exceptions import parse_response_error
from pyowm.utils import timeformatutils, timeutils


class OzoneParser(jsonparser.JSONParser):
    """
    Concrete *JSONParser* implementation building an *Ozone* instance out
    of raw JSON data coming from OWM web API responses.

    """

    def __init__(self):
        pass

    def parse_JSON(self, JSON_string):
        """
        Parses an *Ozone* instance out of raw JSON data. Only certain
        properties of the data are used: if these properties are not found or
        cannot be parsed, an error is issued.

        :param JSON_string: a raw JSON string
        :type JSON_string: str
        :returns: an *Ozone* instance or ``None`` if no data is available
        :raises: *ParseResponseError* if it is impossible to find or parse the
            data needed to build the result, *APIResponseError* if the JSON
            string embeds an HTTP status error (this is an OWM web API 2.5 bug)

        """
        d = json.loads(JSON_string)
        try:
            # -- reference time (strip away Z and T on ISO8601 format)
            ref_t = d['time'].replace('Z', '+00').replace('T', ' ')
            reference_time = timeformatutils._ISO8601_to_UNIXtime(ref_t)

            # -- reception time (now)
            reception_time = timeutils.now('unix')

            # -- location
            lon = float(d['location']['longitude'])
            lat = float(d['location']['latitude'])
            place = location.Location(None, lon, lat, None)

            # -- ozone Dobson Units value
            du_value = float(d['data'])

        except KeyError:
            raise parse_response_error.ParseResponseError(
                      ''.join([__name__, ': impossible to parse UV Index']))

        return ozone.Ozone(reference_time, place, None, du_value, reception_time)

    def __repr__(self):
        return "<%s.%s>" % (__name__, self.__class__.__name__)
