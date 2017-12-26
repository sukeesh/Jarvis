from datetime import datetime
from sqlobject import col, events, SQLObject, AND


class Version(SQLObject):
    def restore(self):
        values = self.sqlmeta.asDict()
        del values['id']
        del values['masterID']
        del values['dateArchived']
        for _col in self.extraCols:
            del values[_col]
        self.masterClass.get(self.masterID).set(**values)

    def nextVersion(self):
        version = self.select(
            AND(self.q.masterID == self.masterID, self.q.id > self.id),
            orderBy=self.q.id)
        if version.count():
            return version[0]
        else:
            return self.master

    def getChangedFields(self):
        next = self.nextVersion()
        columns = self.masterClass.sqlmeta.columns
        fields = []
        for column in columns:
            if column not in ["dateArchived", "id", "masterID"]:
                if getattr(self, column) != getattr(next, column):
                    fields.append(column.title())

        return fields

    @classmethod
    def select(cls, clause=None, *args, **kw):
        if not getattr(cls, '_connection', None):
            cls._connection = cls.masterClass._connection
        return super(Version, cls).select(clause, *args, **kw)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.master, attr)


def getColumns(columns, cls):
    for column, defi in cls.sqlmeta.columnDefinitions.items():
        if column.endswith("ID") and isinstance(defi, col.ForeignKey):
            column = column[:-2]

        # remove incompatible constraints
        kwds = dict(defi._kw)
        for kw in ["alternateID", "unique"]:
            if kw in kwds:
                del kwds[kw]
        columns[column] = defi.__class__(**kwds)

    # ascend heirarchy
    if cls.sqlmeta.parentClass:
        getColumns(columns, cls.sqlmeta.parentClass)


class Versioning(object):
    def __init__(self, extraCols=None):
        if extraCols:
            self.extraCols = extraCols
        else:
            self.extraCols = {}
        pass

    def __addtoclass__(self, soClass, name):
        self.name = name
        self.soClass = soClass

        attrs = {'dateArchived': col.DateTimeCol(default=datetime.now),
                 'master': col.ForeignKey(self.soClass.__name__),
                 'masterClass': self.soClass,
                 'extraCols': self.extraCols
                 }

        getColumns(attrs, self.soClass)

        attrs.update(self.extraCols)

        self.versionClass = type(self.soClass.__name__ + 'Versions',
                                 (Version,),
                                 attrs)

        if '_connection' in self.soClass.__dict__:
            self.versionClass._connection = \
                self.soClass.__dict__['_connection']

        events.listen(self.createTable,
                      soClass, events.CreateTableSignal)
        events.listen(self.rowUpdate, soClass,
                      events.RowUpdateSignal)

    def createVersionTable(self, cls, conn):
        self.versionClass.createTable(ifNotExists=True, connection=conn)

    def createTable(self, soClass, connection, extra_sql, post_funcs):
        assert soClass is self.soClass
        post_funcs.append(self.createVersionTable)

    def rowUpdate(self, instance, kwargs):
        if instance.childName and instance.childName != self.soClass.__name__:
            return  # if you want your child class versioned, version it

        values = instance.sqlmeta.asDict()
        del values['id']
        values['masterID'] = instance.id
        self.versionClass(connection=instance._connection, **values)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return self.versionClass.select(
            self.versionClass.q.masterID == obj.id, connection=obj._connection)
