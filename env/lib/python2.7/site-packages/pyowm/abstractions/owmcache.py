"""
Module containing the abstract PyOWM cache provider
"""

from abc import ABCMeta, abstractmethod


class OWMCache(object):
    """
    A global abstract class representing a caching provider which can be used
    to lookup the JSON responses to the most recently or most frequently issued
    OWM web API requests.
    The purpose of the caching mechanism is to avoid OWM web API requests and
    therefore network traffic: the implementations should be adapted to the
    time/memory requirements of the OWM data clients (i.e: a "slimmer" cache
    with lower lookup times but higher miss rates or a "fatter" cache with
    higher memory consumption and higher hit rates?).
    Subclasses should implement a proper caching algorithms bearing in mind
    that different weather data types may have different change rates: in
    example, observed weather can change very frequently while long-period
    weather forecasts change less frequently.
    External caching mechanisms (eg: memcached, redis, etc..) can be used by
    extending this class into a proper decorator for the correspondent Python
    bindings.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, request_url):
        """
        In case of a hit, returns the JSON string which represents the OWM web
        API response to the request being identified by a specific string URL.

        :param request_url: an URL that uniquely identifies the request whose
            response is to be looked up
        :type request_url: str
        :returns: a JSON str in case of cache hit or ``None`` otherwise

        """
        raise NotImplementedError

    @abstractmethod
    def set(self, request_url, response_json):
        """
        Adds the specified response_json value to the cache using as a lookup
        key the request_url of the request that generated the value.

        :param request_url: the request URL
        :type request_url: str
        :param response_json: the response JSON
        :type response_json: str

        """
        raise NotImplementedError
