import os.path
from pymetabiosis.module import import_module

def test_import_sqlite():
    module = import_module("sqlite")
    module_str = str(module)
    assert module_str.startswith("<module 'sqlite' from ")
