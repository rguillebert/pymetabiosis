from pymetabiosis.module import import_module
from pymetabiosis.wrapper import MetabiosisWrapper

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
    assert repr(ret) == "(u'Yeltsin', 72)"

def test_gettype():
    sqlite3 = import_module("sqlite3")

    assert repr(sqlite3.get_type()) == "<type 'module'>"

def test_convert_return_value():
    builtin = import_module("__builtin__")

    assert builtin.int(32) == 32
    assert builtin.float(3.123) == 3.123
    for s in ['a string']: # TODO 'a string \00yep']:
        assert builtin.str(s) == s
