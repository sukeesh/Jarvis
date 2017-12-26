"""
Exports a SQLObject class (possibly annotated) to a CSV file.
"""
import csv
import os
try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO, BytesIO
import sqlobject
from sqlobject.compat import PY2, string_type

__all__ = ['export_csv', 'export_csv_zip']


def export_csv(soClass, select=None, writer=None, connection=None,
               orderBy=None):
    """
    Export the SQLObject class ``soClass`` to a CSV file.

    ``soClass`` can also be a SelectResults object, as returned by
    ``.select()``.  If it is a class, all objects will be retrieved,
    ordered by ``orderBy`` if given, or the ``.csvOrderBy`` attribute
    if present (but csvOrderBy will only be applied when no select
    result is given).

    You can also pass in select results (or simply a list of
    instances) in ``select`` -- if you have a list of objects (not a
    SelectResults instance, as produced by ``.select()``) then you must
    pass it in with ``select`` and pass the class in as the first
    argument.

    ``writer`` is a ``csv.writer()`` object, or a file-like object.
    If not given, the string of the file will be returned.

    Uses ``connection`` as the data source, if given, otherwise the
    default connection.

    Columns can be annotated with ``.csvTitle`` attributes, which will
    form the attributes of the columns, or 'title' (secondarily), or
    if nothing then the column attribute name.

    If a column has a ``.noCSV`` attribute which is true, then the
    column will be suppressed.

    Additionally a class can have an ``.extraCSVColumns`` attribute,
    which should be a list of strings/tuples.  If a tuple, it should
    be like ``(attribute, title)``, otherwise it is the attribute,
    which will also be the title.  These will be appended to the end
    of the CSV file; the attribute will be retrieved from instances.

    Also a ``.csvColumnOrder`` attribute can be on the class, which is
    the string names of attributes in the order they should be
    presented.
    """

    return_fileobj = None
    if not writer:
        return_fileobj = StringIO()
        writer = csv.writer(return_fileobj)
    elif not hasattr(writer, 'writerow'):
        writer = csv.writer(writer)

    if isinstance(soClass, sqlobject.SQLObject.SelectResultsClass):
        assert select is None, (
            "You cannot pass in a select argument (%r) "
            "and a SelectResults argument (%r) for soClass" %
            (select, soClass))
        select = soClass
        soClass = select.sourceClass
    elif select is None:
        select = soClass.select()
        if getattr(soClass, 'csvOrderBy', None):
            select = select.orderBy(soClass.csvOrderBy)

    if orderBy:
        select = select.orderBy(orderBy)
    if connection:
        select = select.connection(connection)

    _actually_export_csv(soClass, select, writer)

    if return_fileobj:
        # They didn't pass any writer or file object in, so we return
        # the string result:
        return return_fileobj.getvalue()


def _actually_export_csv(soClass, select, writer):
    attributes, titles = _find_columns(soClass)
    writer.writerow(titles)
    for soInstance in select:
        row = [getattr(soInstance, attr)
               for attr in attributes]
        writer.writerow(row)


def _find_columns(soClass):
    order = []
    attrs = {}
    for col in soClass.sqlmeta.columnList:
        if getattr(col, 'noCSV', False):
            continue
        order.append(col.name)
        title = col.name
        if hasattr(col, 'csvTitle'):
            title = col.csvTitle
        elif getattr(col, 'title', None) is not None:
            title = col.title
        attrs[col.name] = title

    for attrDesc in getattr(soClass, 'extraCSVColumns', []):
        if isinstance(attrDesc, (list, tuple)):
            attr, title = attrDesc
        else:
            attr = title = attrDesc
        order.append(attr)
        attrs[attr] = title

    if hasattr(soClass, 'csvColumnOrder'):
        oldOrder = order
        order = soClass.csvColumnOrder
        for attr in order:
            if attr not in oldOrder:
                raise KeyError(
                    "Attribute %r in csvColumnOrder (on class %r) "
                    "does not exist as a column or in .extraCSVColumns "
                    "(I have: %r)" % (attr, soClass, oldOrder))
            oldOrder.remove(attr)
        order.extend(oldOrder)

    titles = [attrs[attr] for attr in order]
    return order, titles


def export_csv_zip(soClasses, file=None, zip=None, filename_prefix='',
                   connection=None):
    """
    Export several SQLObject classes into a .zip file.  Each
    item in the ``soClasses`` list may be a SQLObject class,
    select result, or ``(soClass, select)`` tuple.

    Each file in the zip will be named after the class name (with
    ``.csv`` appended), or using the filename in the ``.csvFilename``
    attribute.

    If ``file`` is given, the zip will be written to that.  ``file``
    may be a string (a filename) or a file-like object.  If not given,
    a string will be returnd.

    If ``zip`` is given, then the files will be written to that zip
    file.

    All filenames will be prefixed with ``filename_prefix`` (which may
    be a directory name, for instance).
    """
    import zipfile
    close_file_when_finished = False
    close_zip_when_finished = True
    return_when_finished = False
    if file:
        if isinstance(file, string_type):
            close_file_when_finished = True
            file = open(file, 'wb')
    elif zip:
        close_zip_when_finished = False
    else:
        return_when_finished = True
        if PY2:
            file = StringIO()
        else:
            # zipfile on python3 requires BytesIO
            file = BytesIO()

    if not zip:
        zip = zipfile.ZipFile(file, mode='w')

    try:
        _actually_export_classes(soClasses, zip, filename_prefix,
                                 connection)
    finally:
        if close_zip_when_finished:
            zip.close()
        if close_file_when_finished:
            file.close()

    if return_when_finished:
        return file.getvalue()


def _actually_export_classes(soClasses, zip, filename_prefix,
                             connection):
    for classDesc in soClasses:
        if isinstance(classDesc, (tuple, list)):
            soClass, select = classDesc
        elif isinstance(classDesc, sqlobject.SQLObject.SelectResultsClass):
            select = classDesc
            soClass = select.sourceClass
        else:
            soClass = classDesc
            select = None
        filename = getattr(soClass, 'csvFilename', soClass.__name__)
        if not os.path.splitext(filename)[1]:
            filename += '.csv'
        filename = filename_prefix + filename
        zip.writestr(filename,
                     export_csv(soClass, select, connection=connection))
