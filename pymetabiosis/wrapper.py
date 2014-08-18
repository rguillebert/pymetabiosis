from pymetabiosis.bindings import lib, ffi
import operator

def convert(obj):
    return converters[type(obj)](obj)

def convert_string(str):
    return ffi.gc(lib.PyString_FromString(ffi.new("char[]", str)), lib.Py_DECREF)

def convert_tuple(obj):
    values = [convert(value) for value in obj]

    return ffi.gc(lib.PyTuple_Pack(len(values), *values), lib.Py_DECREF)

def convert_int(obj):
    return ffi.gc(lib.PyInt_FromLong(obj), lib.Py_DECREF)

def convert_dict(obj):
    dict = ffi.gc(lib.PyDict_New(), lib.Py_DECREF)

    for key, value in obj.iteritems():
        lib.PyDict_SetItem(dict, convert(key), convert(value))

    return dict

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

    def __call__(self, *args, **kwargs):
        arguments_tuple = convert_tuple(args)

        keywordargs = ffi.NULL
        if kwargs:
            keywordargs = convert_dict(kwargs)

        return_value = ffi.gc(lib.PyObject_Call(self.obj, arguments_tuple, keywordargs), lib.Py_DECREF)

        lib.Py_DECREF(arguments_tuple)

        if return_value == ffi.NULL:
            lib.PyErr_Print()
            raise Exception()

        return MetabiosisWrapper(return_value)

    def get_type(self):
        typeobject = ffi.cast("PyObject*", self.obj.ob_type)

        lib.Py_INCREF(typeobject)

        return MetabiosisWrapper(ffi.gc(typeobject, lib.Py_DECREF))

converters = {
    str : convert_string,
    MetabiosisWrapper : operator.attrgetter("obj"),
    tuple : convert_tuple,
    int : convert_int,
    dict : convert_dict,
}
