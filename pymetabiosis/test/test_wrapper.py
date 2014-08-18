from pymetabiosis.module import import_module
from pymetabiosis.wrapper import MetabiosisWrapper

def test_getattr_on_module():
    sqlite = import_module("sqlite")
    assert isinstance(sqlite, MetabiosisWrapper)
    connect = sqlite.connect
    assert isinstance(connect, MetabiosisWrapper)
    assert repr(connect).startswith("<function connect at ")

def test_call_function():
    sqlite = import_module("sqlite")
    connection = sqlite.connect(":memory:")
    assert repr(connection).startswith("<sqlite.main.Connection instance at ")

def test_pass_wrapper_to_function():
    sqlite = import_module("sqlite")
    builtin = import_module("__builtin__")

    string = builtin.str(":memory:")
    connection = sqlite.connect(string)

    assert repr(connection).startswith("<sqlite.main.Connection instance at ")

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
