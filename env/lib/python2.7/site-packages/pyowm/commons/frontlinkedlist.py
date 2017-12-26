"""
Module containing class related to the implementation of linked-list data
structure
"""

import copy
from pyowm.abstractions import linkedlist


class LinkedListNode:
    """
    Class representing an element of the LinkedList

    :param data: the actual data that this node holds
    :type data: object
    :param next: reference to the next LinkedListNode instance in the list
    :type next: LinkedListNode

    """

    def __init__(self, data, next_node):
        self._data = data
        self._next = next_node

    def data(self):
        """
        Returns the data in this node

        :returns: an object
        """
        return self._data

    def next(self):
        """
        Returns the next LinkedListNode in the list

        :returns: a LinkedListNode instance
        """
        return self._next

    def update_next(self, linked_list_node):
        """
        :param linked_list_node: the new reference to the next LinkedListNode
            element
        :type linked_list_node: LinkedListNode

        """
        self._next = linked_list_node

    def __repr__(self):
        return "<%s.%s - data=%s>" % \
            (__name__, self.__class__.__name__, repr(self._data))


class FrontLinkedListIterator(object):
    """
    Iterator over the LinkedListNode elements of a LinkedList class instance.
    The implementation keeps a copy of the iterated list so avoid concurrency
    problems when iterating over it. This can nevertheless be memory-consuming
    when big lists have to be iterated over.

    :param obj: the iterable object (LinkedList)
    :type obj: object
    :returns:  a FrontLinkedListIterator instance

    """
    def __init__(self, obj):
        self._obj = copy.deepcopy(obj)
        self._current_item = self._obj.first_node()
        self._cnt = 0

    def next(self):
        """
        Compatibility for Python 2.x, delegates to function: `__next__()`
        Returns the next *Weather* item

        :returns: the next *Weather* item

        """
        return self.__next__()

    def __next__(self):
        """
        Returns the next LinkedListNode item in the list

        :returns: the data encapuslated into the next LinkedListNode item

        """
        if self._current_item is None:
            raise StopIteration
        result = self._current_item
        self._current_item = result.next()
        return result


class FrontLinkedList(linkedlist.LinkedList):

    """
    Implementation of a linked-list data structure. Insertions are performed at
    the front of the list and so are O(1) while deletions take O(n) because
    they can be performed against any of the linked list's elements.
    Each element in the list is a LinkedListNode instance; after instantiation,
    the list contains no elements.

    :param first_node: reference to the first LinkedListNode element in the
        list
    :type first_node: LinkedListNode
    :param last_node: reference to the last LinkedListNode element in the list
    :type last_node: LinkedListNode

    """
    def __init__(self):
        self._first_node = LinkedListNode(None, None)
        self._last_node = self._first_node
        self._size = 0

    def first_node(self):
        return self._first_node

    def size(self):
        """
        Returns the number of elements in the list

        :returns: an int

        """
        return self._size

    def __iter__(self):
        """
        Creates a FrontLinkedListIterator instance

        :returns: a FrontLinkedListIterator instance
        """
        return FrontLinkedListIterator(self)

    def add(self, data):
        """
        Adds a new data node to the front list. The provided data will be
        encapsulated into a new instance of LinkedListNode class and linked
        list pointers will be updated, as well as list's size.

        :param data: the data to be inserted in the new list node
        :type data: object

        """
        node = LinkedListNode(data, None)
        if self._size == 0:
            self._first_node = node
            self._last_node = node
        else:
            second_node = self._first_node
            self._first_node = node
            self._first_node.update_next(second_node)
        self._size += 1

    def remove(self, data):
        """
        Removes a data node from the list. If the list contains more than one
        node having the same data that shall be removed, then the node having
        the first occurrency of the data is removed.

        :param data: the data to be removed in the new list node
        :type data: object

        """
        current_node = self._first_node
        deleted = False

        if self._size == 0:
            return

        if data == current_node.data():
            # case 1: the list has only one item
            if current_node.next() is None:
                self._first_node = LinkedListNode(None, None)
                self._last_node = self._first_node
                self._size = 0
                return
            # case 2: the list has more than one item
            current_node = current_node.next()
            self._first_node = current_node
            self._size -= 1
            return

        while True:
            if current_node is None:
                deleted = False
                break
            # Check next element's data
            next_node = current_node.next()
            if next_node is not None:
                if data == next_node.data():
                    next_next_node = next_node.next()
                    current_node.update_next(next_next_node)
                    next_node = None
                    deleted = True
                    break
            current_node = current_node.next()
        if deleted:
            self._size -= 1

    def contains(self, data):
        """
        Checks if the provided data is stored in at least one node of the list.

        :param data: the seeked data
        :type data: object
        :returns: a boolean

        """
        for item in self:
            if item.data() == data:
                return True
        return False

    def index_of(self, data):
        """
        Finds the position of a node in the list. The index of the first
        occurrence of the data is returned (indexes start at 0)

        :param data: data of the seeked node
        :type: object
        :returns: the int index or -1 if the node is not in the list

        """
        current_node = self._first_node
        pos = 0
        while current_node:
            if current_node.data() == data:
                return pos
            else:
                current_node = current_node.next()
                pos += 1
        return -1

    def pop(self):
        """
        Removes the last node from the list

        """
        popped = False
        result = None
        current_node = self._first_node
        while not popped:
            next_node = current_node.next()
            next_next_node = next_node.next()
            if not next_next_node:
                self._last_node = current_node
                self._last_node.update_next(None)
                self._size -= 1
                result = next_node.data()
                popped = True
            current_node = next_node
        return result

    def __repr__(self):
        return "<%s.%s - size=%s, first node=%s, last node=%s>" % \
            (__name__, self.__class__.__name__, str(self._size),
             repr(self._first_node), repr(self._last_node))
