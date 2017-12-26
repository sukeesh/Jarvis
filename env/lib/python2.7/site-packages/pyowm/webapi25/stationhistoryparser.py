"""
Module containing a concrete implementation for JSONParser abstract class,
returning a StationHistory instance
"""

import json
import time
from pyowm.webapi25 import stationhistory
from pyowm.abstractions import jsonparser
from pyowm.exceptions import parse_response_error, api_response_error


class StationHistoryParser(jsonparser.JSONParser):
    """
    Concrete *JSONParser* implementation building a *StationHistory* instance
    out of raw JSON data coming from OWM web API responses.

    """

    def __init__(self):
        pass

    def parse_JSON(self, JSON_string):
        """
        Parses a *StationHistory* instance out of raw JSON data. Only certain
        properties of the data are used: if these properties are not found or
        cannot be parsed, an error is issued.

        :param JSON_string: a raw JSON string
        :type JSON_string: str
        :returns: a *StationHistory* instance or ``None`` if no data is
            available
        :raises: *ParseResponseError* if it is impossible to find or parse the
            data needed to build the result, *APIResponseError* if the JSON
            string embeds an HTTP status error (this is an OWM web API 2.5 bug)

        """
        d = json.loads(JSON_string)
        # Check if server returned errors: this check overcomes the lack of use
        # of HTTP error status codes by the OWM API but it's supposed to be
        # deprecated as soon as the API implements a correct HTTP mechanism for
        # communicating errors to the clients. In addition, in this specific
        # case the OWM API responses are the very same either when no results
        # are found for a station and when the station does not exist!
        measurements = {}
        try:
            if 'cod' in d:
                if d['cod'] != "200":
                    raise api_response_error.APIResponseError(
                                              "OWM API: error - response " + \
                                              "payload: " + str(d))
            if str(d['cnt']) == "0":
                return None
            else:
                for item in d['list']:
                    if 'temp' not in item:
                        temp = None
                    elif isinstance(item['temp'], dict):
                        temp = item['temp']['v']
                    else:
                        temp = item['temp']
                    if 'humidity' not in item:
                        hum = None
                    elif isinstance(item['humidity'], dict):
                        hum = item['humidity']['v']
                    else:
                        hum = item['humidity']
                    if 'pressure' not in item:
                        pres = None
                    elif isinstance(item['pressure'], dict):
                        pres = item['pressure']['v']
                    else:
                        pres = item['pressure']
                    if 'rain' in item and isinstance(item['rain']['today'],
                                                     dict):
                        rain = item['rain']['today']['v']
                    else:
                        rain = None
                    if 'wind' in item and isinstance(item['wind']['speed'],
                                                     dict):
                        wind = item['wind']['speed']['v']
                    else:
                        wind = None
                    measurements[item['dt']] = {"temperature": temp,
                                                "humidity": hum,
                                                "pressure": pres,
                                                "rain": rain,
                                                "wind": wind
                                                }
        except KeyError:
            raise parse_response_error.ParseResponseError(__name__ + \
                                     ': impossible to read JSON data')
        current_time = round(time.time())
        return stationhistory.StationHistory(None, None, current_time,
                                             measurements)

    def __repr__(self):
        return "<%s.%s>" % (__name__, self.__class__.__name__)
