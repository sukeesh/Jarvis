"""
Import from a CSV file or directory of files.

CSV files should have a header line that lists columns.  Headers can
also be appended with ``:type`` to indicate the type of the field.
``escaped`` is the default, though it can be overridden by the importer.
Supported types:

``:python``:
    A python expression, run through ``eval()``.  This can be a
    security risk, pass in ``allow_python=False`` if you don't want to
    allow it.

``:int``:
    Integer

``:float``:
    Float

``:str``:
    String

``:escaped``:
    A string with backslash escapes (note that you don't put quotation
    marks around the value)

``:base64``:
    A base64-encoded string

``:date``:
    ISO date, like YYYY-MM-DD; this can also be ``NOW+days`` or
    ``NOW-days``

``:datetime``:
    ISO date/time like YYYY-MM-DDTHH:MM:SS (either T or a space can be
    used to separate the time, and seconds are optional).  This can
    also be ``NOW+seconds`` or ``NOW-seconds``

``:bool``:
    Converts true/false/yes/no/on/off/1/0 to boolean value

``:ref``:
    This will be resolved to the ID of the object named in this column
    (None if the column is empty).  @@: Since there's no ordering,
    there's no way to promise the object already exists.

You can also get back references to the objects if you have a special
``[name]`` column.

Any column named ``[comment]`` or with no name will be ignored.

In any column you can put ``[default]`` to exclude the value and use
whatever default the class wants.  ``[null]`` will use NULL.

Lines that begin with ``[comment]`` are ignored.
"""

import csv
from datetime import datetime, date, timedelta
import os
import time
import types

__all__ = ['load_csv_from_directory',
           'load_csv',
           'create_data']


DEFAULT_TYPE = 'escaped'


def create_data(data, class_getter, keyorder=None):
    """
    Create the ``data``, which is the return value from
    ``load_csv()``.  Classes will be resolved with the callable
    ``class_getter``; or if ``class_getter`` is a module then the
    class names will be attributes of that.

    Returns a dictionary of ``{object_name: object(s)}``, using the
    names from the ``[name]`` columns (if there are any).  If a name
    is used multiple times, you get a list of objects, not a single
    object.

    If ``keyorder`` is given, then the keys will be retrieved in that
    order.  It can be a list/tuple of names, or a sorting function.
    If not given and ``class_getter`` is a module and has a
    ``soClasses`` function, then that will be used for the order.
    """
    objects = {}
    classnames = data.keys()
    if (not keyorder and isinstance(class_getter, types.ModuleType) and
            hasattr(class_getter, 'soClasses')):
        keyorder = [c.__name__ for c in class_getter.soClasses]
    if not keyorder:
        classnames.sort()
    elif isinstance(keyorder, (list, tuple)):
        all = classnames
        classnames = [name for name in keyorder if name in classnames]
        for name in all:
            if name not in classnames:
                classnames.append(name)
    else:
        classnames.sort(keyorder)
    for classname in classnames:
        items = data[classname]
        if not items:
            continue
        if isinstance(class_getter, types.ModuleType):
            soClass = getattr(class_getter, classname)
        else:
            soClass = class_getter(classname)
        for item in items:
            for key, value in item.items():
                if isinstance(value, Reference):
                    resolved = objects.get(value.name)
                    if not resolved:
                        raise ValueError(
                            "Object reference to %r does not have target"
                            % value.name)
                    elif (isinstance(resolved, list) and len(resolved) > 1):
                        raise ValueError(
                            "Object reference to %r is ambiguous (got %r)"
                            % (value.name, resolved))
                    item[key] = resolved.id
            if '[name]' in item:
                name = item.pop('[name]').strip()
            else:
                name = None
            inst = soClass(**item)
            if name:
                if name in objects:
                    if isinstance(objects[name], list):
                        objects[name].append(inst)
                    else:
                        objects[name] = [objects[name], inst]
                else:
                    objects[name] = inst
    return objects


def load_csv_from_directory(directory,
                            allow_python=True, default_type=DEFAULT_TYPE,
                            allow_multiple_classes=True):
    """
    Load the data from all the files in a directory.  Filenames
    indicate the class, with ``general.csv`` for data not associated
    with a class.  Return data just like ``load_csv`` does.

    This might cause problems on case-insensitive filesystems.
    """
    results = {}
    for filename in os.listdir(directory):
        base, ext = os.path.splitext(filename)
        if ext.lower() != '.csv':
            continue
        f = open(os.path.join(directory, filename), 'rb')
        csvreader = csv.reader(f)
        data = load_csv(csvreader, allow_python=allow_python,
                        default_type=default_type,
                        default_class=base,
                        allow_multiple_classes=allow_multiple_classes)
        f.close()
        for classname, items in data.items():
            results.setdefault(classname, []).extend(items)
    return results


def load_csv(csvreader, allow_python=True, default_type=DEFAULT_TYPE,
             default_class=None, allow_multiple_classes=True):
    """
    Loads the CSV file, returning a list of dictionaries with types
    coerced.
    """
    current_class = default_class
    current_headers = None
    results = {}

    for row in csvreader:
        if not [cell for cell in row if cell.strip()]:
            # empty row
            continue

        if row and row[0].strip() == 'CLASS:':
            if not allow_multiple_classes:
                raise ValueError(
                    "CLASS: line in CSV file, but multiple classes "
                    "are not allowed in this file (line: %r)" % row)
            if not row[1:]:
                raise ValueError(
                    "CLASS: in line in CSV file, with no class name "
                    "in next column (line: %r)" % row)
            current_class = row[1]
            current_headers = None
            continue

        if not current_class:
            raise ValueError(
                "No CLASS: line given, and there is no default class "
                "for this file (line: %r)" % row)

        if current_headers is None:
            current_headers = _parse_headers(row, default_type,
                                             allow_python=allow_python)
            continue

        if row[0] == '[comment]':
            continue

        # Pad row with empty strings:
        row += [''] * (len(current_headers) - len(row))
        row_converted = {}
        for value, (name, coercer, args) in zip(row, current_headers):
            if name is None:
                # Comment
                continue
            if value == '[default]':
                continue
            if value == '[null]':
                row_converted[name] = None
                continue
            args = (value,) + args
            row_converted[name] = coercer(*args)

        results.setdefault(current_class, []).append(row_converted)

    return results


def _parse_headers(header_row, default_type, allow_python=True):
    headers = []
    for name in header_row:
        original_name = name
        if ':' in name:
            name, type = name.split(':', 1)
        else:
            type = default_type
        if type == 'python' and not allow_python:
            raise ValueError(
                ":python header given when python headers are not allowed "
                "(with header %r)" % original_name)
        name = name.strip()
        if name == '[comment]' or not name:
            headers.append((None, None, None))
            continue
        type = type.strip().lower()
        if '(' in type:
            type, arg = type.split('(', 1)
            if not arg.endswith(')'):
                raise ValueError(
                    "Arguments (in ()'s) do not end with ): %r"
                    % original_name)
            args = (arg[:-1],)
        else:
            args = ()
        if name == '[name]':
            type = 'str'
        coercer, args = get_coercer(type)
        headers.append((name, coercer, args))
    return headers


_coercers = {}


def get_coercer(type):
    if type not in _coercers:
        raise ValueError(
            "Coercion type %r not known (I know: %s)"
            % (type, ', '.join(_coercers.keys())))
    return _coercers[type]


def register_coercer(type, coercer, *args):
    _coercers[type] = (coercer, args)


def identity(v):
    return v

register_coercer('str', identity)
register_coercer('string', identity)


def decode_string(v, encoding):
    return v.decode(encoding)

register_coercer('escaped', decode_string, 'string_escape')
register_coercer('strescaped', decode_string, 'string_escape')
register_coercer('base64', decode_string, 'base64')

register_coercer('int', int)
register_coercer('float', float)


def parse_python(v):
    return eval(v, {}, {})

register_coercer('python', parse_python)


def parse_date(v):
    v = v.strip()
    if not v:
        return None
    if v.startswith('NOW-') or v.startswith('NOW+'):
        days = int(v[3:])
        now = date.today()
        return now + timedelta(days)
    else:
        parsed = time.strptime(v, '%Y-%m-%d')
        return date.fromtimestamp(time.mktime(parsed))

register_coercer('date', parse_date)


def parse_datetime(v):
    v = v.strip()
    if not v:
        return None
    if v.startswith('NOW-') or v.startswith('NOW+'):
        seconds = int(v[3:])
        now = datetime.now()
        return now + timedelta(0, seconds)
    else:
        fmts = ['%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M',
                '%Y-%m-%d %H:%M']
        for fmt in fmts[:-1]:
            try:
                parsed = time.strptime(v, fmt)
                break
            except ValueError:
                pass
        else:
            parsed = time.strptime(v, fmts[-1])
        return datetime.fromtimestamp(time.mktime(parsed))

register_coercer('datetime', parse_datetime)


class Reference(object):
    def __init__(self, name):
        self.name = name


def parse_ref(v):
    if not v.strip():
        return None
    else:
        return Reference(v)

register_coercer('ref', parse_ref)


def parse_bool(v):
    v = v.strip().lower()
    if v in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif v in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    raise ValueError(
        "Value is not boolean-like: %r" % v)

register_coercer('bool', parse_bool)
register_coercer('boolean', parse_bool)
