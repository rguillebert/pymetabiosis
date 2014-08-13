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

    def __getattr__(self, name):
        c_name = ffi.new("char[]", name)
        py_attr = lib.PyObject_GetAttrString(self.obj, c_name)
        if py_attr == ffi.NULL:
            lib.PyErr_Print()
            raise Exception()
        return MetabiosisWrapper(ffi.gc(py_attr, lib.Py_DECREF))
