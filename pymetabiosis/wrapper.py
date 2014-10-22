import operator
import types
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

def convert_bool(obj):
    return ffi.gc(lib.Py_True, lib.Py_DECREF) \
            if obj else ffi.gc(lib.Py_False, lib.Py_DECREF)

def convert_None(obj):
    return ffi.gc(lib.Py_None, lib.Py_DECREF) # FIXME - check docs

def convert_float(obj):
    return ffi.gc(lib.PyFloat_FromDouble(obj), lib.Py_DECREF)

def convert_dict(obj):
    dict = ffi.gc(lib.PyDict_New(), lib.Py_DECREF)

    for key, value in obj.iteritems():
        lib.PyDict_SetItem(dict, convert(key), convert(value))

    return dict

def convert_list(obj):
    lst = ffi.gc(lib.PyList_New(len(obj)), lib.Py_DECREF)
    for i, x in enumerate(obj):
        lib.PyList_SetItem(lst, i, convert(x))
    return lst


class MetabiosisWrapper(object):
    def __init__(self, obj, noconvert=False):
        self.obj = obj
        self.noconvert = noconvert

    def __repr__(self):
        py_str = ffi.gc(lib.PyObject_Repr(self.obj), lib.Py_DECREF)
        return pypy_convert(py_str)

    def __str__(self):
        py_str = ffi.gc(lib.PyObject_Str(self.obj), lib.Py_DECREF)
        return pypy_convert(py_str)

    def __dir__(self):
        py_lst = ffi.gc(lib.PyObject_Dir(self.obj), lib.Py_DECREF)
        return pypy_convert(py_lst)

    def __getattr__(self, name):
        c_name = ffi.new("char[]", name)
        py_attr = ffi.gc(
                lib.PyObject_GetAttrString(self.obj, c_name),
                lib.Py_DECREF)
        return MetabiosisWrapper(py_attr, self.noconvert)

    def __getitem__(self, key):
        py_res = ffi.gc(
                lib.PyObject_GetItem(self.obj, convert(key)),
                lib.Py_DECREF)
        # TODO - respect self.noconvert ?
        return pypy_convert(py_res)

    def __setitem__(self, key, value):
        lib.PyObject_SetItem(self.obj, convert(key), convert(value))

    def __delitem__(self, key):
        lib.PyObject_DelItem(self.obj, convert(key))

    def __len__(self):
        return lib.PyObject_Size(self.obj)

    def __iter__(self):
        py_iter = ffi.gc(lib.PyObject_GetIter(self.obj), lib.Py_DECREF)
        while True:
            py_next = lib.PyIter_Next(py_iter)
            if py_next is None:
                break
            yield pypy_convert(py_next)

    def __call__(self, *args, **kwargs):
        arguments_tuple = convert_tuple(args)

        keywordargs = ffi.NULL
        if kwargs:
            keywordargs = convert_dict(kwargs)

        return_value = ffi.gc(
                lib.PyObject_Call(self.obj, arguments_tuple, keywordargs),
                lib.Py_DECREF)

        if self.noconvert:
            return MetabiosisWrapper(return_value, self.noconvert)
        else:
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

def pypy_convert_bool(obj):
    return obj == lib.Py_True

def pypy_convert_None(obj):
    return None

def pypy_convert_float(obj):
    return float(lib.PyFloat_AsDouble(obj))

def pypy_convert_string(obj):
    return ffi.string(lib.PyString_AsString(obj))

def pypy_convert_unicode(obj):
    return pypy_convert_string(lib.PyUnicode_AsUTF8String(obj))\
            .decode('utf-8')

def pypy_convert_tuple(obj):
    return tuple(
            pypy_convert(lib.PyTuple_GetItem(obj, i))
            for i in xrange(lib.PyTuple_Size(obj)))

def pypy_convert_dict(obj):
    items = ffi.gc(lib.PyDict_Items(obj), lib.Py_DECREF)
    return dict(pypy_convert_list(items))

def pypy_convert_list(obj):
    return [pypy_convert(lib.PyList_GetItem(obj, i))
            for i in xrange(lib.PyList_Size(obj))]


pypy_to_cpy_converters = {
    MetabiosisWrapper : operator.attrgetter("obj"),
    int : convert_int,
    float : convert_float,
    str : convert_string,
    unicode : convert_unicode,
    tuple : convert_tuple,
    dict : convert_dict,
    list : convert_list,
    bool : convert_bool,
    types.NoneType: convert_None,
}
cpy_to_pypy_converters = {}


def init_cpy_to_pypy_converters():
    global cpy_to_pypy_converters

    builtin = pymetabiosis.module.import_module("__builtin__")
    types = pymetabiosis.module.import_module("types")

    cpy_to_pypy_converters = {
            builtin.int.obj : pypy_convert_int,
            builtin.float.obj : pypy_convert_float,
            builtin.str.obj : pypy_convert_string,
            builtin.unicode.obj : pypy_convert_unicode,
            builtin.tuple.obj : pypy_convert_tuple,
            builtin.dict.obj : pypy_convert_dict,
            builtin.list.obj : pypy_convert_list,
            builtin.bool.obj : pypy_convert_bool,
            types.NoneType.obj : pypy_convert_None,
            }
