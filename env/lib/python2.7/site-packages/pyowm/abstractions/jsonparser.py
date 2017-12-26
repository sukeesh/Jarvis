"""
Module containing an abstract base class for JSON OWM web API responses parsing
"""

from abc import ABCMeta, abstractmethod


class JSONParser(object):
    """
    A global abstract class representing a JSON to object parser.

    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def parse_JSON(self, JSON_string):
        """
        Returns a proper object parsed from the input JSON_string. Subclasses
        know from their specific type which object is to be parsed and returned

        :param JSON_string: a JSON text string
        :type JSON_string: str
        :returns: an object
        :raises: *ParseResponseError* if it is impossible to find or parse the
            data needed to build the resulting object

        """
        raise NotImplementedError
