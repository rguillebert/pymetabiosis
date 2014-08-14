from pymetabiosis.bindings import lib, ffi
import operator

def convert_string(str):
    return ffi.gc(lib.PyString_FromString(ffi.new("char[]", str)), lib.Py_DECREF)

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

    def __call__(self, *args):
        converters_lst = [converters[type(x)] for x in args]
        arguments = [func(value) for value, func in zip(args, converters_lst)]

        arguments_tuple = lib.PyTuple_Pack(len(arguments), *arguments)

        return_value = ffi.gc(lib.PyObject_Call(self.obj, arguments_tuple, ffi.NULL), lib.Py_DECREF)

        lib.Py_DECREF(arguments_tuple)

        if return_value == ffi.NULL:
            lib.PyErr_Print()
            raise Exception()

        return MetabiosisWrapper(return_value)

converters = {str : convert_string, MetabiosisWrapper : operator.attrgetter("obj")}
