"""
Module containing NotFoundError class
"""

import os
from pyowm.exceptions import OWMError


class NotFoundError(OWMError):
    """
    Error class that represents the situation when an entity is not found into
    a collection of entities.

    :param cause: the message of the error
    :type cause: str
    :returns: a *NotFoundError* instance
    """
    def __init__(self, message):
        self._message = message

    def __str__(self):
        """Redefine __str__ hook for pretty-printing"""
        return ''.join(['The searched item was not found.', os.linesep,
                        'Reason: ', self._message.decode('utf-8')])
