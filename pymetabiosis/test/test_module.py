import pytest
from pymetabiosis.module import import_module

def test_import_sqlite():
    module = import_module("sqlite3")
    module_str = str(module)
    assert module_str.startswith("<module 'sqlite3' from ")

def test_import_error():
    with pytest.raises(ImportError):
        import_module('thereisnosuchmodule4sure')
