"""
Module containing APIResponseError class
"""

import os
from pyowm.exceptions import OWMError


class APIResponseError(OWMError):
    """
    Error class that represents HTTP error status codes in OWM web API
    responses.

    :param cause: the message of the error
    :type cause: str
    :returns: a *APIResponseError* instance
    """
    def __init__(self, message):
        self._message = message

    def __str__(self):
        """Redefine __str__ hook for pretty-printing"""
        return ''.join(['An error HTTP status code was returned by the ' + \
                        'OWM API', os.linesep, 'Reason: ',
                        self._message]).decode('utf-8')
