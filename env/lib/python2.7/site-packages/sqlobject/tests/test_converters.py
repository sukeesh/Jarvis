from datetime import timedelta

from sqlobject.col import SODateTimeCol, SOTimeCol
from sqlobject.converters import registerConverter, sqlrepr, \
    quote_str, unquote_str
from sqlobject.sqlbuilder import SQLExpression, SQLObjectField, \
    Select, Insert, Update, Delete, Replace, \
    SQLTrueClauseClass, SQLConstant, SQLPrefix, SQLCall, SQLOp, \
    _LikeQuoted


class SOTestClass:

    def __repr__(self):
        return '<SOTestClass>'


def SOTestClassConverter(value, db):
    return repr(value)

registerConverter(SOTestClass, SOTestClassConverter)


class NewSOTestClass:

    __metaclass__ = type

    def __repr__(self):
        return '<NewSOTestClass>'


def NewSOTestClassConverter(value, db):
    return repr(value)

registerConverter(NewSOTestClass, NewSOTestClassConverter)


def _sqlrepr(self, db):
    return '<%s>' % self.__class__.__name__

SQLExpression.__sqlrepr__ = _sqlrepr

############################################################
# Tests
############################################################


def test_simple_string():
    assert sqlrepr('A String', 'firebird') == "'A String'"


def test_string_newline():
    assert sqlrepr('A String\nAnother', 'postgres') == "E'A String\\nAnother'"
    assert sqlrepr('A String\nAnother', 'sqlite') == "'A String\nAnother'"


def test_string_tab():
    assert sqlrepr('A String\tAnother', 'postgres') == "E'A String\\tAnother'"


def test_string_r():
    assert sqlrepr('A String\rAnother', 'postgres') == "E'A String\\rAnother'"


def test_string_b():
    assert sqlrepr('A String\bAnother', 'postgres') == "E'A String\\bAnother'"


def test_string_000():
    assert sqlrepr('A String\000Another', 'postgres') == \
        "E'A String\\0Another'"


def test_string_():
    assert sqlrepr('A String\tAnother', 'postgres') == "E'A String\\tAnother'"
    assert sqlrepr('A String\'Another', 'firebird') == "'A String''Another'"


def test_simple_unicode():
    assert sqlrepr(u'A String', 'postgres') == "'A String'"


def test_integer():
    assert sqlrepr(10) == "10"


def test_float():
    assert sqlrepr(10.01) == "10.01"


def test_none():
    assert sqlrepr(None) == "NULL"


def test_list():
    assert sqlrepr(['one', 'two', 'three'], 'postgres') == \
        "('one', 'two', 'three')"


def test_tuple():
    assert sqlrepr(('one', 'two', 'three'), 'postgres') == \
        "('one', 'two', 'three')"


def test_bool():
    assert sqlrepr(True, 'postgres') == "'t'"
    assert sqlrepr(False, 'postgres') == "'f'"
    assert sqlrepr(True, 'mysql') == "1"
    assert sqlrepr(False, 'mysql') == "0"


def test_datetime():
    from datetime import datetime, date, time
    if SODateTimeCol.datetimeFormat.find('.%f') > 0:
        assert sqlrepr(datetime(2005, 7, 14, 13, 31, 2)) == \
            "'2005-07-14 13:31:02.000000'"
    else:
        assert sqlrepr(datetime(2005, 7, 14, 13, 31, 2)) == \
            "'2005-07-14 13:31:02'"
    assert sqlrepr(date(2005, 7, 14)) == "'2005-07-14'"
    if SOTimeCol.timeFormat.find('.%f') > 0:
        assert sqlrepr(time(13, 31, 2)) == "'13:31:02.000000'"
    else:
        assert sqlrepr(time(13, 31, 2)) == "'13:31:02'"
    # now dates before 1900
    if SODateTimeCol.datetimeFormat.find('.%f') > 0:
        assert sqlrepr(datetime(1428, 7, 14, 13, 31, 2)) == \
            "'1428-07-14 13:31:02.000000'"
    else:
        assert sqlrepr(datetime(1428, 7, 14, 13, 31, 2)) == \
            "'1428-07-14 13:31:02'"
    assert sqlrepr(date(1428, 7, 14)) == "'1428-07-14'"


def test_instance():
    instance = SOTestClass()
    assert sqlrepr(instance) == repr(instance)


def test_newstyle():
    instance = NewSOTestClass()
    assert sqlrepr(instance) == repr(instance)


def test_sqlexpr():
    instance = SQLExpression()
    assert sqlrepr(instance) == repr(instance)


def test_sqlobjectfield():
    instance = SQLObjectField('test', 'test', 'test', None, None)
    assert sqlrepr(instance) == repr(instance)


def test_select():
    instance = Select('test')
    assert sqlrepr(instance, 'mysql') == "SELECT test"


def test_insert():
    # Single column, no keyword arguments.
    instance = Insert('test', [('test',)])
    assert sqlrepr(instance, 'mysql') == "INSERT INTO test VALUES ('test')"

    # Multiple columns, no keyword arguments.
    instance2 = Insert('test', [('1st', '2nd', '3th', '4th')])
    assert sqlrepr(instance2, 'postgres') == \
        "INSERT INTO test VALUES ('1st', '2nd', '3th', '4th')"

    # Multiple rows, multiple columns, "valueList" keyword argument.
    instance3 = Insert('test',
                       valueList=[('a1', 'b1'), ('a2', 'b2'), ('a3', 'b3')])
    assert sqlrepr(instance3, 'sqlite') == \
        "INSERT INTO test VALUES ('a1', 'b1'), ('a2', 'b2'), ('a3', 'b3')"

    # Multiple columns, "values" keyword argument.
    instance4 = Insert('test', values=('v1', 'v2', 'v3'))
    assert sqlrepr(instance4, 'mysql') == \
        "INSERT INTO test VALUES ('v1', 'v2', 'v3')"

    # Single column, "valueList" keyword argument.
    instance5 = Insert('test', valueList=[('v1',)])
    assert sqlrepr(instance5, 'mysql') == "INSERT INTO test VALUES ('v1')"

    # Multiple rows, Multiple columns, template.
    instance6 = Insert('test',
                       valueList=[('a1', 'b1'), ('a2', 'b2')],
                       template=['col1', 'col2'])
    assert sqlrepr(instance6, 'mysql') == \
        "INSERT INTO test (col1, col2) VALUES ('a1', 'b1'), ('a2', 'b2')"

    # Multiple columns, implicit template (dictionary value).
    instance7 = Insert('test', valueList=[{'col1': 'a1', 'col2': 'b1'}])
    assert sqlrepr(instance7, 'mysql') == \
        "INSERT INTO test (col1, col2) VALUES ('a1', 'b1')"

    # Multiple rows, Multiple columns, implicit template.
    instance8 = Insert('test', valueList=[{'col1': 'a1', 'col2': 'b1'},
                                          {'col1': 'a2', 'col2': 'b2'}])
    assert sqlrepr(instance8, 'mysql') == \
        "INSERT INTO test (col1, col2) VALUES ('a1', 'b1'), ('a2', 'b2')"


def test_update():
    instance = Update('test', {'test': 'test'})
    assert sqlrepr(instance, 'mysql') == "UPDATE test SET test='test'"


def test_delete():
    instance = Delete('test', None)
    assert sqlrepr(instance, 'mysql') == "DELETE FROM test"


def test_replace():
    instance = Replace('test', {'test': 'test'})
    assert sqlrepr(instance, 'mysql') == "REPLACE test SET test='test'"


def test_trueclause():
    instance = SQLTrueClauseClass()
    assert sqlrepr(instance) == repr(instance)


def test_op():
    instance = SQLOp('and', 'this', 'that')
    assert sqlrepr(instance, 'mysql') == "(('this') AND ('that'))"


def test_call():
    instance = SQLCall('test', ('test',))
    assert sqlrepr(instance, 'mysql') == "'test'('test')"


def test_constant():
    instance = SQLConstant('test')
    assert sqlrepr(instance) == repr(instance)


def test_prefix():
    instance = SQLPrefix('test', 'test')
    assert sqlrepr(instance, 'mysql') == "test 'test'"


def test_dict():
    assert sqlrepr({"key": "value"}, "sqlite") == "('key')"


def test_sets():
    try:
        set
    except NameError:
        pass
    else:
        assert sqlrepr(set([1])) == "(1)"


def test_timedelta():
    assert sqlrepr(timedelta(seconds=30 * 60)) == \
        "INTERVAL '0 days 1800 seconds'"


def test_quote_unquote_str():
    assert quote_str('test%', 'postgres') == "'test%'"
    assert quote_str('test%', 'sqlite') == "'test%'"
    assert quote_str('test\%', 'postgres') == "E'test\\%'"
    assert quote_str('test\\%', 'sqlite') == "'test\%'"
    assert unquote_str("'test%'") == 'test%'
    assert unquote_str("'test\\%'") == 'test\\%'
    assert unquote_str("E'test\\%'") == 'test\\%'


def test_like_quoted():
    assert sqlrepr(_LikeQuoted('test'), 'postgres') == "'test'"
    assert sqlrepr(_LikeQuoted('test'), 'sqlite') == "'test'"
    assert sqlrepr(_LikeQuoted('test%'), 'postgres') == r"E'test\\%'"
    assert sqlrepr(_LikeQuoted('test%'), 'sqlite') == r"'test\%'"
