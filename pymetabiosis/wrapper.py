from pymetabiosis.bindings import lib, ffi

class MetabiosisWrapper(object):
    def __init__(self, obj):
        self.obj = obj

    def __repr__(self):
        py_str = lib.PyObject_Repr(self.obj)
        if py_str == ffi.NULL:
            lib.PyErr_Print()
            raise Exception()
        c_str = lib.PyString_AsString(py_str)
        lib.Py_DECREF(py_str)
        return ffi.string(c_str)
