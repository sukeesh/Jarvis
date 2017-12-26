"""
Module containing ParseResponseError class
"""
import os
from pyowm.exceptions import OWMError


class ParseResponseError(OWMError):
    """
    Error class that represents failures when parsing payload data in HTTP
    responses sent by the OWM web API.

    :param cause: the message of the error
    :type cause: str
    :returns: a *ParseResponseError* instance
    """
    def __init__(self, message):
        self._message = message

    def __str__(self):
        """Redefine __str__ hook for pretty-printing"""
        return ''.join(['Exception in parsing OWM web API response',
                        os.linesep, 'Reason: ', self._message.decode('utf-8')])
