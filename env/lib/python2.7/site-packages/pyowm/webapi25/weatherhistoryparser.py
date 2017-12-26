"""
Module containing a concrete implementation for JSONParser abstract class,
returning a list of Weather objects
"""

import json
from pyowm.webapi25 import weather
from pyowm.abstractions import jsonparser
from pyowm.exceptions import parse_response_error, api_response_error


class WeatherHistoryParser(jsonparser.JSONParser):
    """
    Concrete *JSONParser* implementation building a list of *Weather* instances
    out of raw JSON data coming from OWM web API responses.

    """

    def __init__(self):
        pass

    def parse_JSON(self, JSON_string):
        """
        Parses a list of *Weather* instances out of raw JSON data. Only certain
        properties of the data are used: if these properties are not found or
        cannot be parsed, an error is issued.

        :param JSON_string: a raw JSON string
        :type JSON_string: str
        :returns: a list of *Weather* instances or ``None`` if no data is
            available
        :raises: *ParseResponseError* if it is impossible to find or parse the
            data needed to build the result, *APIResponseError* if the JSON
            string embeds an HTTP status error (this is an OWM web API 2.5 bug)

        """
        d = json.loads(JSON_string)
        # Check if server returned errors: this check overcomes the lack of use
        # of HTTP error status codes by the OWM API 2.5. This mechanism is
        # supposed to be deprecated as soon as the API fully adopts HTTP for
        # conveying errors to the clients
        if 'message' in d and 'cod' in d:
            if d['cod'] == "404":
                print("OWM API: data not found - response payload: " + \
                    json.dumps(d))
                return None
            elif d['cod'] != "200":
                raise api_response_error.APIResponseError(
                                      "OWM API: error - response payload: " + \
                                       json.dumps(d))
        # Handle the case when no results are found
        if 'cnt' in d and d['cnt'] == "0":
            return []
        else:
            if 'list' in d:
                try:
                    return [weather.weather_from_dictionary(item) \
                            for item in d['list']]
                except KeyError:
                    raise parse_response_error.ParseResponseError(
                              ''.join([__name__, ': impossible to read ' \
                                              'weather info from JSON data'])
                          )
            else:
                raise parse_response_error.ParseResponseError(
                              ''.join([__name__, ': impossible to read ' \
                                              'weather list from JSON data'])
                      )

    def __repr__(self):
        return "<%s.%s>" % (__name__, self.__class__.__name__)
