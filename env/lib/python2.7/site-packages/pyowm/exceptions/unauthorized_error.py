"""
Module containing Unauthorized class
"""

import os
from pyowm.exceptions import OWMError


class UnauthorizedError(OWMError):
    """
    Error class that represents the situation when an entity cannot be retrieved
    due to user subscription unsufficient capabilities.

    :param cause: the message of the error
    :type cause: str
    :returns: a *UnauthorizedError* instance
    """
    def __init__(self, message):
        self._message = message

    def __str__(self):
        """Redefine __str__ hook for pretty-printing"""
        return ''.join(['Your API subscription level does not allow to perform '
                        'this operation', os.linesep,
                        'Reason: ', self._message.decode('utf-8')])
