# encoding: utf-8
import pytest
from pymetabiosis.module import import_module
from pymetabiosis.wrapper import MetabiosisWrapper, pypy_convert

def test_getattr_on_module():
    sqlite = import_module("sqlite3")
    assert isinstance(sqlite, MetabiosisWrapper)
    connect = sqlite.connect
    assert isinstance(connect, MetabiosisWrapper)
    assert repr(connect).startswith("<built-in function connect>")

def test_call_function():
    sqlite = import_module("sqlite3")
    connection = sqlite.connect(":memory:")
    assert repr(connection).startswith("<sqlite3.Connection object at ")

def test_pass_wrapper_to_function():
    sqlite = import_module("sqlite3")

    connection = sqlite.connect(":memory:")

    assert repr(connection).startswith("<sqlite3.Connection object at ")

def test_sqlite():
    # Taken from Python 2.7's sqlite doc
    sqlite3 = import_module("sqlite3")

    con = sqlite3.connect(":memory:")
    cur = con.cursor()
    cur.execute("create table people (name_last, age)")

    who = "Yeltsin"
    age = 72

    cur.execute("insert into people values (?, ?)", (who, age))

    cur.execute("select * from people where name_last=:who and age=:age", {"who": who, "age": age})

    ret = cur.fetchone()
    assert ret == (u'Yeltsin', 72)

def test_gettype():
    sqlite3 = import_module("sqlite3")

    assert repr(sqlite3.get_type()) == "<type 'module'>"

def test_convert_return_value():
    builtin = import_module("__builtin__")
    operator = import_module("operator")

    assert builtin.int(32) == 32
    assert builtin.float(3.123) == 3.123

    for s in ['a string']: # TODO 'a string \00yep']:
        assert builtin.str(s) == s

    u = u"some буквы are странные"
    assert builtin.unicode(u) == u

    t = (1, (2.3,))
    assert builtin.tuple(t) == t

    d = {'a': 'b', 1: 2}
    assert builtin.dict(d) == d

    lst = ['a', 1, [2]]
    assert builtin.list(lst) == lst

    assert builtin.bool(True) is True
    assert builtin.bool(False) is False

    assert builtin.bool(None) is False
    assert operator.eq(None, None) is True
    assert operator.eq(None, False) is False

def test_exceptions():
    builtin = import_module("__builtin__")

    with pytest.raises(AttributeError):
        builtin.foo

    with pytest.raises(ValueError): # TODO UnicodeDecodeError
        print builtin.unicode('\124\323')

def test_no_convert():
    operator = import_module("operator")
    functools = import_module("functools")
    builtin = import_module("__builtin__", noconvert=True)

    lst = builtin.list()

    part = functools.partial(operator.iadd, lst)
    part([1, 2, 3])

    assert pypy_convert(lst.obj) == [1, 2, 3]
