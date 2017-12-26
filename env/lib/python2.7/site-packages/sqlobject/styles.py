import re


__all__ = ["Style", "MixedCaseUnderscoreStyle", "DefaultStyle",
           "MixedCaseStyle"]


class Style(object):

    """
    The base Style class, and also the simplest implementation.  No
    translation occurs -- column names and attribute names match,
    as do class names and table names (when using auto class or
    schema generation).
    """

    def __init__(self, pythonAttrToDBColumn=None,
                 dbColumnToPythonAttr=None,
                 pythonClassToDBTable=None,
                 dbTableToPythonClass=None,
                 idForTable=None,
                 longID=False):
        if pythonAttrToDBColumn:
            self.pythonAttrToDBColumn = \
                lambda a, s=self: pythonAttrToDBColumn(s, a)
        if dbColumnToPythonAttr:
            self.dbColumnToPythonAttr = \
                lambda a, s=self: dbColumnToPythonAttr(s, a)
        if pythonClassToDBTable:
            self.pythonClassToDBTable = \
                lambda a, s=self: pythonClassToDBTable(s, a)
        if dbTableToPythonClass:
            self.dbTableToPythonClass = \
                lambda a, s=self: dbTableToPythonClass(s, a)
        if idForTable:
            self.idForTable = lambda a, s=self: idForTable(s, a)
        self.longID = longID

    def pythonAttrToDBColumn(self, attr):
        return attr

    def dbColumnToPythonAttr(self, col):
        return col

    def pythonClassToDBTable(self, className):
        return className

    def dbTableToPythonClass(self, table):
        return table

    def idForTable(self, table):
        if self.longID:
            return self.tableReference(table)
        else:
            return 'id'

    def pythonClassToAttr(self, className):
        return lowerword(className)

    def instanceAttrToIDAttr(self, attr):
        return attr + "ID"

    def instanceIDAttrToAttr(self, attr):
        return attr[:-2]

    def tableReference(self, table):
        return table + "_id"


class MixedCaseUnderscoreStyle(Style):

    """
    This is the default style.  Python attributes use mixedCase,
    while database columns use underscore_separated.
    """

    def pythonAttrToDBColumn(self, attr):
        return mixedToUnder(attr)

    def dbColumnToPythonAttr(self, col):
        return underToMixed(col)

    def pythonClassToDBTable(self, className):
        return className[0].lower() \
            + mixedToUnder(className[1:])

    def dbTableToPythonClass(self, table):
        return table[0].upper() \
            + underToMixed(table[1:])

    def pythonClassToDBTableReference(self, className):
        return self.tableReference(self.pythonClassToDBTable(className))

    def tableReference(self, table):
        return table + "_id"

DefaultStyle = MixedCaseUnderscoreStyle


class MixedCaseStyle(Style):

    """
    This style leaves columns as mixed-case, and uses long
    ID names (like ProductID instead of simply id).
    """

    def pythonAttrToDBColumn(self, attr):
        return capword(attr)

    def dbColumnToPythonAttr(self, col):
        return lowerword(col)

    def dbTableToPythonClass(self, table):
        return capword(table)

    def tableReference(self, table):
        return table + "ID"

defaultStyle = DefaultStyle()


def getStyle(soClass, dbConnection=None):
    if dbConnection is None:
        if hasattr(soClass, '_connection'):
            dbConnection = soClass._connection
    if hasattr(soClass.sqlmeta, 'style') and soClass.sqlmeta.style:
        return soClass.sqlmeta.style
    elif dbConnection and dbConnection.style:
        return dbConnection.style
    else:
        return defaultStyle


############################################################
# Text utilities
############################################################


_mixedToUnderRE = re.compile(r'[A-Z]+')


def mixedToUnder(s):
    if s.endswith('ID'):
        return mixedToUnder(s[:-2] + "_id")
    trans = _mixedToUnderRE.sub(mixedToUnderSub, s)
    if trans.startswith('_'):
        trans = trans[1:]
    return trans


def mixedToUnderSub(match):
    m = match.group(0).lower()
    if len(m) > 1:
        return '_%s_%s' % (m[:-1], m[-1])
    else:
        return '_%s' % m


def capword(s):
    return s[0].upper() + s[1:]


def lowerword(s):
    return s[0].lower() + s[1:]


_underToMixedRE = re.compile('_.')


def underToMixed(name):
    if name.endswith('_id'):
        return underToMixed(name[:-3] + "ID")
    return _underToMixedRE.sub(lambda m: m.group(0)[1].upper(),
                               name)
