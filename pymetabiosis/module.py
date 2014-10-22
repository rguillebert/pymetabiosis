from pymetabiosis.bindings import ffi, lib
from pymetabiosis.wrapper import MetabiosisWrapper

def import_module(name, noconvert=False):
    module_object = lib.PyImport_ImportModule(name)
    return MetabiosisWrapper(ffi.gc(module_object, lib.Py_DECREF), noconvert)
