"""
Declarative objects.

Declarative objects have a simple protocol: you can use classes in
lieu of instances and they are equivalent, and any keyword arguments
you give to the constructor will override those instance variables.
(So if a class is received, we'll simply instantiate an instance with
no arguments).

You can provide a variable __unpackargs__ (a list of strings), and if
the constructor is called with non-keyword arguments they will be
interpreted as the given keyword arguments.

If __unpackargs__ is ('*', name), then all the arguments will be put
in a variable by that name.

You can define a __classinit__(cls, new_attrs) method, which will be
called when the class is created (including subclasses).  Note: you
can't use super() in __classinit__ because the class isn't bound to a
name.  As an analog to __classinit__, Declarative adds
__instanceinit__ which is called with the same argument (new_attrs).
This is like __init__, but after __unpackargs__ and other factors have
been taken into account.

If __mutableattributes__ is defined as a sequence of strings, these
attributes will not be shared between superclasses and their
subclasses.  E.g., if you have a class variable that contains a list
and you append to that list, changes to subclasses will effect
superclasses unless you add the attribute here.

Also defines classinstancemethod, which acts as either a class method
or an instance method depending on where it is called.
"""

import copy
from . import events
from sqlobject.compat import with_metaclass

import itertools
counter = itertools.count()

__all__ = ('classinstancemethod', 'DeclarativeMeta', 'Declarative')


class classinstancemethod(object):
    """
    Acts like a class method when called from a class, like an
    instance method when called by an instance.  The method should
    take two arguments, 'self' and 'cls'; one of these will be None
    depending on how the method was called.
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, type=None):
        return _methodwrapper(self.func, obj=obj, type=type)


class _methodwrapper(object):

    def __init__(self, func, obj, type):
        self.func = func
        self.obj = obj
        self.type = type

    def __call__(self, *args, **kw):
        assert 'self' not in kw and 'cls' not in kw, (
            "You cannot use 'self' or 'cls' arguments to a "
            "classinstancemethod")
        return self.func(*((self.obj, self.type) + args), **kw)

    def __repr__(self):
        if self.obj is None:
            return ('<bound class method %s.%s>'
                    % (self.type.__name__, self.func.__name__))
        else:
            return ('<bound method %s.%s of %r>'
                    % (self.type.__name__, self.func.__name__, self.obj))


class DeclarativeMeta(type):

    def __new__(meta, class_name, bases, new_attrs):
        post_funcs = []
        early_funcs = []
        events.send(events.ClassCreateSignal,
                    bases[0], class_name, bases, new_attrs,
                    post_funcs, early_funcs)
        cls = type.__new__(meta, class_name, bases, new_attrs)
        for func in early_funcs:
            func(cls)
        if '__classinit__' in new_attrs:
            if hasattr(cls.__classinit__, '__func__'):
                cls.__classinit__ = staticmethod(cls.__classinit__.__func__)
            else:
                cls.__classinit__ = staticmethod(cls.__classinit__)
        cls.__classinit__(cls, new_attrs)
        for func in post_funcs:
            func(cls)
        return cls


class Declarative(with_metaclass(DeclarativeMeta, object)):

    __unpackargs__ = ()

    __mutableattributes__ = ()

    __restrict_attributes__ = None

    def __classinit__(cls, new_attrs):
        cls.declarative_count = next(counter)
        for name in cls.__mutableattributes__:
            if name not in new_attrs:
                setattr(cls, copy.copy(getattr(cls, name)))

    def __instanceinit__(self, new_attrs):
        if self.__restrict_attributes__ is not None:
            for name in new_attrs:
                if name not in self.__restrict_attributes__:
                    raise TypeError(
                        '%s() got an unexpected keyword argument %r'
                        % (self.__class__.__name__, name))
        for name, value in new_attrs.items():
            setattr(self, name, value)
        if 'declarative_count' not in new_attrs:
            self.declarative_count = next(counter)

    def __init__(self, *args, **kw):
        if self.__unpackargs__ and self.__unpackargs__[0] == '*':
            assert len(self.__unpackargs__) == 2, \
                "When using __unpackargs__ = ('*', varname), " \
                "you must only provide a single variable name " \
                "(you gave %r)" % self.__unpackargs__
            name = self.__unpackargs__[1]
            if name in kw:
                raise TypeError(
                    "keyword parameter '%s' was given by position and name"
                    % name)
            kw[name] = args
        else:
            if len(args) > len(self.__unpackargs__):
                raise TypeError(
                    '%s() takes at most %i arguments (%i given)'
                    % (self.__class__.__name__,
                       len(self.__unpackargs__),
                       len(args)))
            for name, arg in zip(self.__unpackargs__, args):
                if name in kw:
                    raise TypeError(
                        "keyword parameter '%s' was given by position and name"
                        % name)
                kw[name] = arg
        if '__alsocopy' in kw:
            for name, value in kw['__alsocopy'].items():
                if name not in kw:
                    if name in self.__mutableattributes__:
                        value = copy.copy(value)
                    kw[name] = value
            del kw['__alsocopy']
        self.__instanceinit__(kw)

    def __call__(self, *args, **kw):
        kw['__alsocopy'] = self.__dict__
        return self.__class__(*args, **kw)

    @classinstancemethod
    def singleton(self, cls):
        if self:
            return self
        name = '_%s__singleton' % cls.__name__
        if not hasattr(cls, name):
            setattr(cls, name, cls(declarative_count=cls.declarative_count))
        return getattr(cls, name)

    @classinstancemethod
    def __repr__(self, cls):
        if self:
            name = '%s object' % self.__class__.__name__
            v = self.__dict__.copy()
        else:
            name = '%s class' % cls.__name__
            v = cls.__dict__.copy()
        if 'declarative_count' in v:
            name = '%s %i' % (name, v['declarative_count'])
            del v['declarative_count']
        # @@: simplifying repr:
        # v = {}
        names = v.keys()
        args = []
        for n in self._repr_vars(names):
            args.append('%s=%r' % (n, v[n]))
        if not args:
            return '<%s>' % name
        else:
            return '<%s %s>' % (name, ' '.join(args))

    @staticmethod
    def _repr_vars(dictNames):
        names = [n for n in dictNames
                 if not n.startswith('_') and
                 n != 'declarative_count']
        names.sort()
        return names


def setup_attributes(cls, new_attrs):
    for name, value in new_attrs.items():
        if hasattr(value, '__addtoclass__'):
            value.__addtoclass__(cls, name)
