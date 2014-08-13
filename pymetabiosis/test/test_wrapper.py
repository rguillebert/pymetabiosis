from pymetabiosis.module import import_module
from pymetabiosis.wrapper import MetabiosisWrapper

def test_getattr_on_module():
    sqlite = import_module("sqlite")
    assert isinstance(sqlite, MetabiosisWrapper)
    connect = sqlite.connect
    assert isinstance(connect, MetabiosisWrapper)
    assert repr(connect).startswith("<function connect at ")
