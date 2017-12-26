"""
Bound attributes are attributes that are bound to a specific class and
a specific name.  In SQLObject a typical example is a column object,
which knows its name and class.

A bound attribute should define a method ``__addtoclass__(added_class,
name)`` (attributes without this method will simply be treated as
normal).  The return value is ignored; if the attribute wishes to
change the value in the class, it must call ``setattr(added_class,
name, new_value)``.

BoundAttribute is a class that facilitates lazy attribute creation.
"""
from __future__ import absolute_import

from . import declarative
from . import events

__all__ = ['BoundAttribute', 'BoundFactory']


class BoundAttribute(declarative.Declarative):

    """
    This is a declarative class that passes all the values given to it
    to another object.  So you can pass it arguments (via
    __init__/__call__) or give it the equivalent of keyword arguments
    through subclassing.  Then a bound object will be added in its
    place.

    To hook this other object in, override ``make_object(added_class,
    name, **attrs)`` and maybe ``set_object(added_class, name,
    **attrs)`` (the default implementation of ``set_object``
    just resets the attribute to whatever ``make_object`` returned).

    Also see ``BoundFactory``.
    """

    _private_variables = (
        '_private_variables',
        '_all_attributes',
        '__classinit__',
        '__addtoclass__',
        '_add_attrs',
        'set_object',
        'make_object',
        'clone_in_subclass',
    )

    _all_attrs = ()
    clone_for_subclass = True

    def __classinit__(cls, new_attrs):
        declarative.Declarative.__classinit__(cls, new_attrs)
        cls._all_attrs = cls._add_attrs(cls, new_attrs)

    def __instanceinit__(self, new_attrs):
        declarative.Declarative.__instanceinit__(self, new_attrs)
        self.__dict__['_all_attrs'] = self._add_attrs(self, new_attrs)

    @staticmethod
    def _add_attrs(this_object, new_attrs):
        private = this_object._private_variables
        all_attrs = list(this_object._all_attrs)
        for key in new_attrs.keys():
            if key.startswith('_') or key in private:
                continue
            if key not in all_attrs:
                all_attrs.append(key)
        return tuple(all_attrs)

    @declarative.classinstancemethod
    def __addtoclass__(self, cls, added_class, attr_name):
        me = self or cls
        attrs = {}
        for name in me._all_attrs:
            attrs[name] = getattr(me, name)
        attrs['added_class'] = added_class
        attrs['attr_name'] = attr_name
        obj = me.make_object(**attrs)

        if self.clone_for_subclass:
            def on_rebind(new_class_name, bases, new_attrs,
                          post_funcs, early_funcs):
                def rebind(new_class):
                    me.set_object(
                        new_class, attr_name,
                        me.make_object(**attrs))
                post_funcs.append(rebind)
            events.listen(receiver=on_rebind, soClass=added_class,
                          signal=events.ClassCreateSignal, weak=False)

        me.set_object(added_class, attr_name, obj)

    @classmethod
    def set_object(cls, added_class, attr_name, obj):
        setattr(added_class, attr_name, obj)

    @classmethod
    def make_object(cls, added_class, attr_name, *args, **attrs):
        raise NotImplementedError

    def __setattr__(self, name, value):
        self.__dict__['_all_attrs'] = self._add_attrs(self, {name: value})
        self.__dict__[name] = value


class BoundFactory(BoundAttribute):

    """
    This will bind the attribute to whatever is given by
    ``factory_class``.  This factory should be a callable with the
    signature ``factory_class(added_class, attr_name, *args, **kw)``.

    The factory will be reinvoked (and the attribute rebound) for
    every subclassing.
    """

    factory_class = None
    _private_variables = (
        BoundAttribute._private_variables + ('factory_class',))

    def make_object(cls, added_class, attr_name, *args, **kw):
        return cls.factory_class(added_class, attr_name, *args, **kw)
