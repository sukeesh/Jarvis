"""
Test the default styles, to guarantee consistency.
"""

from sqlobject import ForeignKey, MixedCaseStyle, MixedCaseUnderscoreStyle, \
    SQLObject, StringCol, Style

# Hash of styles versus the database names resulting from 'columns' below.
columns = ["ABCUpper", "abc_lower", "ABCamelCaseColumn"]
styles = {
    Style: columns,
    MixedCaseUnderscoreStyle: ["abc_upper", "abc_lower",
                               "ab_camel_case_column"],
    MixedCaseStyle: ["ABCUpper", "Abc_lower", "ABCamelCaseColumn"],
}

# Hash of styles versus the database names
# resulting from a foreign key named 'FKey'.
fkey = ForeignKey("DefaultStyleTest", name="FKey")
fkeys = {
    Style: "FKeyID",
    MixedCaseUnderscoreStyle: "f_key_id",
    MixedCaseStyle: "FKeyID",
}


def make_columns():
    global columns
    columns = []
    for col_name in columns:
        columns.append(StringCol(name=col_name, length=10))


def do_col_test(DefaultStyleTest, style, dbnames):
    DefaultStyleTest.sqlmeta.style = style()
    for col, old_dbname in zip(columns, dbnames):
        DefaultStyleTest.sqlmeta.addColumn(col)
        try:
            new_dbname = DefaultStyleTest.sqlmeta.columns[col.name].dbName
            assert new_dbname == old_dbname
        finally:
            if col.name in DefaultStyleTest.sqlmeta.columns:
                DefaultStyleTest.sqlmeta.delColumn(col)


def do_fkey_test(DefaultStyleTest, style, dbname):
    DefaultStyleTest.sqlmeta.style = style()
    DefaultStyleTest.sqlmeta.addColumn(fkey)
    try:
        assert list(DefaultStyleTest.sqlmeta.columns.keys())[0] == "FKeyID"
        assert list(DefaultStyleTest.sqlmeta.columns.values())[0].dbName == \
            dbname
    finally:
        DefaultStyleTest.sqlmeta.delColumn(fkey)


class DefaultStyleTest(SQLObject):
    pass


def test_default_styles():
    make_columns()
    for style in styles:
        do_col_test(DefaultStyleTest, style, styles[style])
        do_fkey_test(DefaultStyleTest, style, fkeys[style])
