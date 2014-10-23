# encoding: utf-8
import pytest
from pymetabiosis.module import import_module
from pymetabiosis.wrapper import MetabiosisWrapper, pypy_convert, applevel

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

def test_getitem_setitem_delitem():
    builtin = import_module("__builtin__", noconvert=True)

    d = builtin.dict({1: 'foo', (1, 'a'): 'zoo'})
    with pytest.raises(KeyError):
        d[2]
    assert pypy_convert(d[1].obj) == 'foo'
    assert pypy_convert(d[(1, 'a')].obj) == 'zoo'

    key, lst = (1, 2), ['a', 'b']
    d[key] = lst
    assert pypy_convert(d[key].obj) == lst

    with pytest.raises(TypeError):
        d[[1, 2]] = 0

    del d[1]
    with pytest.raises(KeyError):
        d[1]

    with pytest.raises(KeyError):
        del d[2]

def test_str_repr_dir():
    builtin = import_module("__builtin__", noconvert=True)

    assert str(builtin.None) == 'None'
    assert str(builtin.str('a')) == 'a'
    assert repr(builtin.str('a')) == "'a'"

    assert set(['rjust', 'rpartition', 'rstrip', '__le__'])\
            .issubset(dir(builtin.str('a')))

def test_len():
    builtin = import_module("__builtin__", noconvert=True)
    lst = builtin.list([1, 'a'])
    assert len(lst) == 2
    assert len(builtin.list()) == 0
    assert len(builtin.str('abc')) == 3

    with pytest.raises(TypeError):
        len(builtin.iter([1]))

def test_iter():
    builtin = import_module("__builtin__", noconvert=True)
    assert [pypy_convert(x.obj) for x in builtin.list([1, 'a'])] == [1, 'a']
    assert pypy_convert(list(builtin.iter(['a']))[0].obj) == 'a'
    with pytest.raises(TypeError):
        builtin.iter(1)

def test_exceptions():
    builtin = import_module("__builtin__")

    with pytest.raises(AttributeError):
        builtin.foo

    with pytest.raises(ValueError): # TODO UnicodeDecodeError
        builtin.unicode('\124\323')

def test_no_convert():
    operator = import_module("operator")
    functools = import_module("functools")
    builtin = import_module("__builtin__", noconvert=True)

    lst = builtin.list()

    part = functools.partial(operator.iadd, lst)
    part([1, 2, 3])

    assert pypy_convert(lst.obj) == [1, 2, 3]

def test_applevel():
    fn = applevel('''
def f():
    return 3
return f
''', noconvert=False)
    assert fn() == 3

def test_opaque_objects():

    class Point(object):
        _pymetabiosis_wrap = True
        def __init__(self, x, y):
            self.x = x
            self.y = y

    builtin = import_module("__builtin__")
    builtin_noconvert = import_module("__builtin__", noconvert=True)
    p1, p2 = Point(1.0, 2.0), Point(3.0, -1.0)

    lst = builtin.list([p1, p2])
    assert lst == [p1, p2]

    lst_cpy = builtin_noconvert.list([p1, p2])
    assert pypy_convert(lst_cpy[0].obj) == p1
    assert pypy_convert(lst_cpy[1].obj) == p2
    lst_cpy.reverse()
    assert pypy_convert(lst_cpy[1].obj) == p1
    assert pypy_convert(lst_cpy[0].obj) == p2
