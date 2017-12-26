from sqlobject import IntCol, SQLObject, StringCol
from sqlobject.compat import PY2
from sqlobject.sqlbuilder import AND, CONCAT, Delete, Insert, SQLOp, Select, \
    Union, Update, const, func, sqlrepr
from sqlobject.tests.dbtest import getConnection, raises, setupClass


class SOTestSQLBuilder(SQLObject):
    name = StringCol()
    so_value = IntCol()


def test_Select():
    setupClass(SOTestSQLBuilder)

    select1 = Select([const.id, func.MAX(const.salary)],
                     staticTables=['employees'])
    assert sqlrepr(select1) == 'SELECT id, MAX(salary) FROM employees'

    select2 = Select([SOTestSQLBuilder.q.name, SOTestSQLBuilder.q.so_value])
    assert sqlrepr(select2) == \
        'SELECT so_test_sql_builder.name, so_test_sql_builder.so_value ' \
        'FROM so_test_sql_builder'

    union = Union(select1, select2)
    assert sqlrepr(union) == \
        'SELECT id, MAX(salary) FROM employees ' \
        'UNION SELECT so_test_sql_builder.name, ' \
        'so_test_sql_builder.so_value ' \
        'FROM so_test_sql_builder'

    union = Union(SOTestSQLBuilder.select().queryForSelect())
    assert sqlrepr(union) == \
        'SELECT so_test_sql_builder.id, so_test_sql_builder.name, ' \
        'so_test_sql_builder.so_value FROM so_test_sql_builder WHERE 1 = 1'


def test_empty_AND():
    assert AND() is None
    assert AND(True) is True

    # sqlrepr() is needed because AND() returns an SQLExpression that overrides
    # comparison. The following
    #     AND('x', 'y') == "foo bar"
    # is True! (-: Eeek!
    assert sqlrepr(AND(1, 2)) == sqlrepr(SQLOp("AND", 1, 2)) == "((1) AND (2))"
    assert sqlrepr(AND(1, 2, '3'), "sqlite") == \
        sqlrepr(SQLOp("AND", 1, SQLOp("AND", 2, '3')), "sqlite") == \
        "((1) AND ((2) AND ('3')))"


def test_modulo():
    setupClass(SOTestSQLBuilder)
    assert sqlrepr(SOTestSQLBuilder.q.so_value % 2 == 0, 'mysql') == \
        "((MOD(so_test_sql_builder.so_value, 2)) = (0))"
    assert sqlrepr(SOTestSQLBuilder.q.so_value % 2 == 0, 'sqlite') == \
        "(((so_test_sql_builder.so_value) % (2)) = (0))"


def test_division():
    SOTestSQLBuilder(name='test', so_value=-11)
    assert sqlrepr(SOTestSQLBuilder.q.so_value / 4 == -2.75, 'mysql') == \
        "(((so_test_sql_builder.so_value) / (4)) = (-2.75))"
    assert sqlrepr(SOTestSQLBuilder.q.so_value // 4 == -3, 'mysql') == \
        "((FLOOR(((so_test_sql_builder.so_value) / (4)))) = (-3))"


def test_str_or_sqlrepr():
    select = Select(['id', 'name'], staticTables=['employees'],
                    where='value>0', orderBy='id')
    assert sqlrepr(select, 'sqlite') == \
        'SELECT id, name FROM employees WHERE value>0 ORDER BY id'

    select = Select(['id', 'name'], staticTables=['employees'],
                    where='value>0', orderBy='id', lazyColumns=True)
    assert sqlrepr(select, 'sqlite') == \
        'SELECT id FROM employees WHERE value>0 ORDER BY id'

    insert = Insert('employees', values={'id': 1, 'name': 'test'})
    assert sqlrepr(insert, 'sqlite') == \
        "INSERT INTO employees (id, name) VALUES (1, 'test')"

    update = Update('employees', {'name': 'test'}, where='id=1')
    assert sqlrepr(update, 'sqlite') == \
        "UPDATE employees SET name='test' WHERE id=1"

    update = Update('employees', {'name': 'test', 'age': 42}, where='id=1')
    assert sqlrepr(update, 'sqlite') == \
        "UPDATE employees SET age=42, name='test' WHERE id=1"

    delete = Delete('employees', where='id=1')
    assert sqlrepr(delete, 'sqlite') == \
        "DELETE FROM employees WHERE id=1"

    raises(TypeError, Delete, 'employees')

    delete = Delete('employees', where=None)
    assert sqlrepr(delete, 'sqlite') == \
        "DELETE FROM employees"


def test_CONCAT():
    setupClass(SOTestSQLBuilder)
    SOTestSQLBuilder(name='test', so_value=42)

    assert sqlrepr(CONCAT('a', 'b'), 'mysql') == "CONCAT('a', 'b')"
    assert sqlrepr(CONCAT('a', 'b'), 'mssql') == "'a' + 'b'"
    assert sqlrepr(CONCAT('a', 'b'), 'sqlite') == "'a' || 'b'"
    assert sqlrepr(CONCAT('prefix', SOTestSQLBuilder.q.name), 'mysql') == \
        "CONCAT('prefix', so_test_sql_builder.name)"
    assert sqlrepr(CONCAT('prefix', SOTestSQLBuilder.q.name), 'sqlite') == \
        "'prefix' || so_test_sql_builder.name"

    select = Select([CONCAT(SOTestSQLBuilder.q.name, '-suffix')],
                    staticTables=['so_test_sql_builder'])
    connection = getConnection()
    rows = connection.queryAll(connection.sqlrepr(select))
    result = rows[0][0]
    if not PY2 and not isinstance(result, str):
        result = result.decode('ascii')
    assert result == "test-suffix"
