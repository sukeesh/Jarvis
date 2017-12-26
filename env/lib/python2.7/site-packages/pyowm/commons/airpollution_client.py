# Python 2.x/3.x compatibility imports
try:
    from urllib.error import HTTPError, URLError
    from urllib.parse import urlencode
except ImportError:
    from urllib2 import HTTPError, URLError
    from urllib import urlencode

import socket
from pyowm.exceptions import api_call_error, not_found_error, unauthorized_error
from pyowm.utils import timeformatutils
from pyowm.webapi25.configuration25 import ROOT_POLLUTION_API_URL, \
    CO_INDEX_URL, OZONE_URL


class AirPollutionHttpClient(object):

    """
    An HTTP client class for the OWM Air Pollution web API. The class can
    leverage a caching mechanism

    :param API_key: a Unicode object representing the OWM Air Pollution web API key
    :type API_key: Unicode
    :param cache: an *OWMCache* concrete instance that will be used to \
         cache OWM Air Pollution web API responses.
    :type cache: an *OWMCache* concrete instance

    """

    def __init__(self, API_key, cache):
        self._API_key = API_key
        self._cache = cache
        self._API_root_URL = ROOT_POLLUTION_API_URL

    def _trim_to(self, date_object, interval):
        if interval == 'minute':
            return date_object.strftime('%Y-%m-%dT%H:%MZ')
        elif interval == 'hour':
            return date_object.strftime('%Y-%m-%dT%HZ')
        elif interval == 'day':
            return date_object.strftime('%Y-%m-%dZ')
        elif interval == 'month':
            return date_object.strftime('%Y-%mZ')
        elif interval == 'year':
            return date_object.strftime('%YZ')
        else:
            raise ValueError("The interval provided for the search "
                             "window is invalid")

    def _lookup_cache_or_invoke_API(self, cache, API_full_url, timeout):
        cached = cache.get(API_full_url)
        if cached:
            return cached
        else:
            try:
                try:
                    from urllib.request import urlopen
                except ImportError:
                    from urllib2 import urlopen
                response = urlopen(API_full_url, None, timeout)
            except HTTPError as e:
                if '401' in str(e):
                    raise unauthorized_error.UnauthorizedError('Invalid API key')
                if '404' in str(e):
                    raise not_found_error.NotFoundError('The resource was not found')
                if '502' in str(e):
                    raise api_call_error.BadGatewayError(str(e), e)
                raise api_call_error.APICallError(str(e), e)
            except URLError as e:
                raise api_call_error.APICallError(str(e), e)
            else:
                data = response.read().decode('utf-8')
                cache.set(API_full_url, data)
                return data

    def get_coi(self, params_dict, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """
        Invokes the CO Index endpoint

        :param params_dict: dict of parameters
        :param timeout: how many seconds to wait for connection establishment \
            (defaults to ``socket._GLOBAL_DEFAULT_TIMEOUT``)
        :type timeout: int
        :returns: a string containing raw JSON data
        :raises: *ValueError*, *APICallError*

        """
        lat = str(params_dict['lat'])
        lon = str(params_dict['lon'])
        start = params_dict['start']
        interval = params_dict['interval']

        # build request URL
        url_template = '%s%s/%s,%s/%s.json?appid=%s'
        if start is None:
            timeref = 'current'
        else:
            if interval is None:
                timeref = self._trim_to(
                    timeformatutils.to_date(start), 'year')
            else:
                timeref = self._trim_to(
                    timeformatutils.to_date(start), interval)

        url = url_template % (ROOT_POLLUTION_API_URL, CO_INDEX_URL, lat, lon,
                              timeref, self._API_key)
        return self._lookup_cache_or_invoke_API(self._cache, url, timeout)

    def get_o3(self, params_dict, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """
        Invokes the O3 Index endpoint

        :param params_dict: dict of parameters
        :param timeout: how many seconds to wait for connection establishment \
            (defaults to ``socket._GLOBAL_DEFAULT_TIMEOUT``)
        :type timeout: int
        :returns: a string containing raw JSON data
        :raises: *ValueError*, *APICallError*

        """
        lat = str(params_dict['lat'])
        lon = str(params_dict['lon'])
        start = params_dict['start']
        interval = params_dict['interval']

        # build request URL
        url_template = '%s%s/%s,%s/%s.json?appid=%s'
        if start is None:
            timeref = 'current'
        else:
            if interval is None:
                timeref = self._trim_to(
                    timeformatutils.to_date(start), 'year')
            else:
                timeref = self._trim_to(
                    timeformatutils.to_date(start), interval)

        url = url_template % (ROOT_POLLUTION_API_URL, OZONE_URL, lat, lon,
                              timeref, self._API_key)
        return self._lookup_cache_or_invoke_API(self._cache, url, timeout)

    def __repr__(self):
        return "<%s.%s - cache=%s>" % \
               (__name__, self.__class__.__name__, repr(self._cache))