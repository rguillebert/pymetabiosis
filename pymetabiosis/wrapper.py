import operator
import pymetabiosis.module
from pymetabiosis.bindings import lib, ffi

def convert(obj):
    return pypy_to_cpy_converters[type(obj)](obj)

def convert_string(s):
    return ffi.gc(lib.PyString_FromString(ffi.new("char[]", s)), lib.Py_DECREF)

def convert_unicode(u):
    return ffi.gc(
            lib.PyUnicode_FromString(ffi.new("char[]", u.encode('utf-8'))),
            lib.Py_DECREF)

def convert_tuple(obj):
    values = [convert(value) for value in obj]

    return ffi.gc(lib.PyTuple_Pack(len(values), *values), lib.Py_DECREF)

def convert_int(obj):
    return ffi.gc(lib.PyInt_FromLong(obj), lib.Py_DECREF)

def convert_float(obj):
    return ffi.gc(lib.PyFloat_FromDouble(obj), lib.Py_DECREF)

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

        return pypy_convert(return_value)

    def get_type(self):
        typeobject = ffi.cast("PyObject*", self.obj.ob_type)

        lib.Py_INCREF(typeobject)

        return MetabiosisWrapper(ffi.gc(typeobject, lib.Py_DECREF))

def pypy_convert(obj):
    type = MetabiosisWrapper(obj).get_type().obj
    if type in cpy_to_pypy_converters:
        return cpy_to_pypy_converters[type](obj)
    else:
        return MetabiosisWrapper(obj)

def pypy_convert_int(obj):
    return int(lib.PyLong_AsLong(obj))

def pypy_convert_float(obj):
    return float(lib.PyFloat_AsDouble(obj))

def pypy_convert_string(obj):
    return ffi.string(lib.PyString_AsString(obj))

def pypy_convert_tuple(obj):
    return tuple(
            pypy_convert(lib.PyTuple_GetItem(obj, i))
            for i in xrange(lib.PyTuple_Size(obj)))

def pypy_convert_unicode(obj):
    return pypy_convert_string(lib.PyUnicode_AsUTF8String(obj))\
            .decode('utf-8')

pypy_to_cpy_converters = {
    str : convert_string,
    unicode : convert_unicode,
    MetabiosisWrapper : operator.attrgetter("obj"),
    tuple : convert_tuple,
    int : convert_int,
    float : convert_float,
    dict : convert_dict,
}
cpy_to_pypy_converters = {}


def init_cpy_to_pypy_converters():
    global cpy_to_pypy_converters

    builtin = pymetabiosis.module.import_module("__builtin__")

    cpy_to_pypy_converters = {
            builtin.int.obj : pypy_convert_int,
            builtin.float.obj : pypy_convert_float,
            builtin.str.obj : pypy_convert_string,
            builtin.unicode.obj : pypy_convert_unicode,
            builtin.tuple.obj : pypy_convert_tuple,
            }
