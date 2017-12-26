from sqlobject import IntCol, SQLObject, StringCol


########################################
# Columns order
########################################


class SOColumnsOrder(SQLObject):
    name = StringCol()
    surname = StringCol()
    parname = StringCol()
    age = IntCol()


def test_columns_order():
    column_names = [c.name for c in SOColumnsOrder.sqlmeta.columnList]
    assert column_names == ['name', 'surname', 'parname', 'age']
