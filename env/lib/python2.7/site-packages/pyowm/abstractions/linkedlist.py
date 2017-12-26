"""
Module containing abstractions for defining a linked list data structure
"""

from abc import ABCMeta, abstractmethod


class LinkedList(object):
    """
    An abstract class representing a Linked List data structure. Each element
    in the list should contain data and a reference to the next element in the
    list.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def size(self):
        """
        Returns the number of elements in the list

        :returns: an int

        """
        raise NotImplementedError

    @abstractmethod
    def add(self, data):
        """
        Adds a new node to the list. Implementations should decide where
        to put this new element (at the top, in the middle or at the end of
        the list) and should therefore update pointers to next elements and
        the list's size.

        :param data: the data to be inserted in the new list node
        :type data: object

        """
        raise NotImplementedError

    @abstractmethod
    def remove(self, data):
        """
        Removes a node from the list. Implementations should decide the
        policy to be followed when list items having the same data are to be
        removed, and should therefore update pointers to next elements and
        the list's size.

        :param data: the data to be removed in the new list node
        :type data: object

        """
        raise NotImplementedError

    @abstractmethod
    def contains(self, data):
        """
        Checks if the provided data is stored in at least one node of the list.

        :param data: data of the seeked node
        :type data: object
        :returns: a boolean

        """
        raise NotImplementedError

    @abstractmethod
    def index_of(self, data):
        """
        Finds the position of a node in the list. The index of the first
        occurrence of the data is returned (indexes start at 0)

        :param data: data of the seeked node
        :type: object
        :returns: the int index or -1 if the node is not in the list

        """
        raise NotImplementedError

    @abstractmethod
    def pop(self):
        """
        Removes the last node from the list

        :returns: the object data that was stored in the last node
        """
        raise NotImplementedError
