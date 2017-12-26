"""
Module containing the abstract PyOWM library main entry point interface
"""

from abc import ABCMeta, abstractmethod


class OWM(object):
    """
    A global abstract class representing the OWM web API. Every query to the
    API is done programmatically via a concrete instance of this class.
    Subclasses should provide a method for every OWM web API endpoint.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_API_key(self):
        """
        Returns the OWM API key

        :returns: the OWM API key string

        """
        raise NotImplementedError

    @abstractmethod
    def set_API_key(self, API_key):
        """
        Updates the OWM API key

        :param API_key: the new value for the OWM API key
        :type API_key: str

        """
        raise NotImplementedError

    @abstractmethod
    def get_API_version(self):
        """
        Returns the currently supported OWM web API version

        :returns: the OWM web API version string

        """
        raise NotImplementedError

    @abstractmethod
    def get_version(self):
        """
        Returns the current version of the PyOWM library

        :returns: the current PyOWM library version string

        """
        raise NotImplementedError

    @abstractmethod
    def is_API_online(self):
        """
        Returns ``True`` if the OWM web API is currently online. A short
        timeout is used to determine API service availability.

        :returns: bool

        """
        raise NotImplementedError