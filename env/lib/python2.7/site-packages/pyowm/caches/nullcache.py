"""
Module containing a null-object cache for OWM web API responses
"""

from pyowm.abstractions import owmcache


class NullCache(owmcache.OWMCache):

    """
    A null-object implementation of the *OWMCache* abstract class

    """

    def __init__(self):
        pass

    def get(self, request_url):
        """
        Always returns ``None`` (nothing will ever be cached or looked up!)

        :param request_url: the request URL
        :type request_url: str
        :returns: ``None``

        """
        return None

    def set(self, request_url, response_json):
        """
        Does nothing.

        :param request_url: the request URL
        :type request_url: str
        :param response_json: the response JSON
        :type response_json: str

        """
        pass

    def __repr__(self):
        return "<%s.%s>" % (__name__, self.__class__.__name__)
