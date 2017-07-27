"""
Module containing a concrete implementation for JSONParser abstract class,
returning a list of Station instances
"""

import json

from pyowm.abstractions.jsonparser import JSONParser
from pyowm.webapi25.stationparser import StationParser
from pyowm.exceptions.parse_response_error import ParseResponseError
from pyowm.exceptions.api_response_error import APIResponseError


class StationListParser(JSONParser):
    """
    Concrete *JSONParser* implementation building a list of *Station*
    instances out of raw JSON data coming from OWM web API responses.

    """

    def parse_JSON(self, JSON_string):
        """
        Parses a list of *Station* instances out of raw JSON data. Only
        certain properties of the data are used: if these properties are not
        found or cannot be parsed, an error is issued.

        :param JSON_string: a raw JSON string
        :type JSON_string: str
        :returns: a list of *Station* instances or ``None`` if no data is
            available
        :raises: *ParseResponseError* if it is impossible to find or parse the
            data needed to build the result, *APIResponseError* if the OWM API
            returns a HTTP status error (this is an OWM web API 2.5 bug)

        """
        d = json.loads(JSON_string)
        station_parser = StationParser()
        return [station_parser.parse_JSON(json.dumps(item)) for item in d]
