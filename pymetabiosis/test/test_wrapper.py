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
