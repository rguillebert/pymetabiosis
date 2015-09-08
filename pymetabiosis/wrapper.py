import operator
import types
from __pypy__ import identity_dict
import pymetabiosis.module
from pymetabiosis.bindings import lib, ffi, exceptions


def convert(obj):
    _type = type(obj)
    if _type in pypy_to_cpy_converters:
        try:
            return pypy_to_cpy_converters[_type](obj)
        except NoConvertError:
            pass
    if getattr(obj, '_pymetabiosis_wrap', None):
        return convert_unknown(obj)
    raise NoConvertError(_type)

def convert_string(s):
    return ffi.gc(lib.PyString_FromString(ffi.new("char[]", s)), lib.Py_DECREF)

def convert_unicode(u):
    return ffi.gc(
            lib.PyUnicode_FromString(ffi.new("char[]", u.encode('utf-8'))),
            lib.Py_DECREF)

def convert_tuple(values, convert_items=True):
    if convert_items:
        values = [convert(value) for value in values]

    return ffi.gc(lib.PyTuple_Pack(len(values), *values), lib.Py_DECREF)

def convert_int(obj):
    return ffi.gc(lib.PyInt_FromLong(obj), lib.Py_DECREF)

def convert_bool(obj):
    py_obj = lib.Py_True if obj else lib.Py_False
    lib.Py_INCREF(py_obj)
    return ffi.gc(py_obj, lib.Py_DECREF)

def convert_None(obj):
    lib.Py_INCREF(lib.Py_None)
    return ffi.gc(lib.Py_None, lib.Py_DECREF)

def convert_float(obj):
    return ffi.gc(lib.PyFloat_FromDouble(obj), lib.Py_DECREF)

def convert_dict(obj, convert_values=True):
    dict = ffi.gc(lib.PyDict_New(), lib.Py_DECREF)

    for key, value in obj.iteritems():
        if convert_values:
            value = convert(value)
        lib.PyDict_SetItem(dict, convert(key), value)

    return dict

def convert_list(obj):
    lst = ffi.gc(lib.PyList_New(len(obj)), lib.Py_DECREF)
    for i, x in enumerate(obj):
        lib.PyList_SetItem(lst, i, convert(x))
    return lst

def convert_slice(obj):
    return ffi.gc(
            lib.PySlice_New(
                convert(obj.start), convert(obj.stop), convert(obj.step)),
            lib.Py_DECREF)

def convert_type(obj):
    try:
        return pypy_to_cpy_types[obj]
    except KeyError:
        raise NoConvertError


@ffi.callback("PyObject*(PyObject*, PyObject*, PyObject*)")
def callback(py_self, py_args, py_kwargs):
    args = () if py_args == ffi.NULL else pypy_convert(py_args)
    kwargs = {} if py_kwargs == ffi.NULL else pypy_convert(py_kwargs)
    fn = pypy_convert(py_self)
    try:
        result = fn(*args, **kwargs)
        return convert(result)
    except Exception as e:
        default_message = "Exception in pymetabiosis callback"
        for py_exc_type, exc_type in reversed(exceptions):
            if isinstance(e, exc_type):
                lib.PyErr_SetString(
                        py_exc_type, ffi.new("char[]", default_message))
                return ffi.NULL
        lib.PyErr_SetString(lib.PyExc_Exception,
                ffi.new("char[]", default_message))
        return ffi.NULL


py_method = ffi.new("PyMethodDef*", dict(
    ml_name=ffi.new("char[]", "pypy_callback"),
    ml_meth=callback,
    ml_flags=lib.METH_VARARGS | lib.METH_KEYWORDS,
    ml_doc=ffi.new("char[]", "")
    ))

def convert_function(obj):
    return lib.PyCFunction_New(py_method, convert_unknown(obj))


class MetabiosisWrapper(object):
    def __init__(self, obj, noconvert=False):
        self.__dict__['_cpyobj'] = obj
        self.__dict__['_noconvert'] = noconvert

    def __abs__(self):
        return self._maybe_pypy_convert(cpy_operator.abs(self))

    def __add__(self, other):
        return self._maybe_pypy_convert(cpy_operator.add(self, other))

    def __and__(self, other):
        return self._maybe_pypy_convert(cpy_operator.and_(self, other))

    def __contains__(self, item):
        return self._maybe_pypy_convert(cpy_operator.contains(self, item))

    def __delslice__(self, a, b):
        return self._maybe_pypy_convert(cpy_operator.delslice(self, a, b))

    def __div__(self, other):
        return self._maybe_pypy_convert(cpy_operator.div(self, other))

    def __eq__(self, other):
        return self._maybe_pypy_convert(cpy_operator.eq(self, other))

    def __floordiv__(self, other):
        return self._maybe_pypy_convert(cpy_operator.floordiv(self, other))

    def __ge__(self, other):
        return self._maybe_pypy_convert(cpy_operator.ge(self, other))

    def __getslice__(self, a, b):
        return self._maybe_pypy_convert(cpy_operator.getslice(self, a, b))

    def __gt__(self, other):
        return self._maybe_pypy_convert(cpy_operator.gt(self, other))

    def __iadd__(self, other):
        return self._maybe_pypy_convert(cpy_operator.iadd(self, other))

    def __iand__(self, other):
        return self._maybe_pypy_convert(cpy_operator.iand(self, other))

    def __idiv__(self, other):
        return self._maybe_pypy_convert(cpy_operator.idiv(self, other))

    def __ifloordiv__(self, other):
        return self._maybe_pypy_convert(cpy_operator.ifloordiv(self, other))

    def __ilshift__(self, other):
        return self._maybe_pypy_convert(cpy_operator.ilshift(self, other))

    def __imod__(self, other):
        return self._maybe_pypy_convert(cpy_operator.imod(self, other))

    def __imul__(self, other):
        return self._maybe_pypy_convert(cpy_operator.imul(self, other))

    def __index__(self):
        """ __index__ must always return an int. """
        return pypy_convert_int(cpy_operator.index(self)._cpyobj)

    def __invert__(self):
        return self._maybe_pypy_convert(cpy_operator.invert(self))

    def __ior__(self, other):
        return self._maybe_pypy_convert(cpy_operator.ior(self, other))

    def __ipow__(self, other):
        return self._maybe_pypy_convert(cpy_operator.ipow(self, other))

    def __irshift__(self, other):
        return self._maybe_pypy_convert(cpy_operator.irshift(self, other))

    def __isub__(self, other):
        return self._maybe_pypy_convert(cpy_operator.isub(self, other))

    def __itruediv__(self, other):
        return self._maybe_pypy_convert(cpy_operator.itruediv(self, other))

    def __ixor__(self, other):
        return self._maybe_pypy_convert(cpy_operator.ixor(self, other))

    def __le__(self, other):
        return self._maybe_pypy_convert(cpy_operator.le(self, other))

    def __lshift__(self, other):
        return self._maybe_pypy_convert(cpy_operator.lshift(self, other))

    def __lt__(self, other):
        return self._maybe_pypy_convert(cpy_operator.lt(self, other))

    def __mod__(self, other):
        return self._maybe_pypy_convert(cpy_operator.mod(self, other))

    def __mul__(self, other):
        return self._maybe_pypy_convert(cpy_operator.mul(self, other))

    def __ne__(self, other):
        return self._maybe_pypy_convert(cpy_operator.ne(self, other))

    def __neg__(self):
        return self._maybe_pypy_convert(cpy_operator.neg(self))

    def __or__(self, other):
        return self._maybe_pypy_convert(cpy_operator.or_(self, other))

    def __pos__(self):
        return self._maybe_pypy_convert(cpy_operator.pos(self))

    def __pow__(self, other):
        return self._maybe_pypy_convert(cpy_operator.pow(self, other))

    def __radd__(self, other):
        return self._maybe_pypy_convert(cpy_operator.add(other, self))

    def __rand__(self, other):
        return self._maybe_pypy_convert(cpy_operator.and_(other, self))

    def __rdiv__(self, other):
        return self._maybe_pypy_convert(cpy_operator.div(other, self))

    def __rdivmod__(self, other):
        return self._maybe_pypy_convert(cpy_operator.divmod(other, self))

    def __rfloordiv__(self, other):
        return self._maybe_pypy_convert(cpy_operator.floordiv(other, self))

    def __rlshift__(self, other):
        return self._maybe_pypy_convert(cpy_operator.lshift(other, self))

    def __rmod__(self, other):
        return self._maybe_pypy_convert(cpy_operator.mod(other, self))

    def __rmul__(self, other):
        return self._maybe_pypy_convert(cpy_operator.mul(other, self))

    def __ror__(self, other):
        return self._maybe_pypy_convert(cpy_operator.or_(other, self))

    def __rpow__(self, other):
        return self._maybe_pypy_convert(cpy_operator.pow(other, self))

    def __rrshift__(self, other):
        return self._maybe_pypy_convert(cpy_operator.rshift(other, self))

    def __rxor__(self, other):
        return self._maybe_pypy_convert(cpy_operator.xor(other, self))

    def __rshift__(self, other):
        return self._maybe_pypy_convert(cpy_operator.rshift(self, other))

    def __rsub__(self, other):
        return self._maybe_pypy_convert(cpy_operator.sub(other, self))

    def __rtruediv__(self, other):
        return self._maybe_pypy_convert(cpy_operator.truediv(other, self))

    def __setslice__(self, a, b, value):
        return self._maybe_pypy_convert(cpy_operator.setslice(self, a, b, value))

    def __sub__(self, other):
        return self._maybe_pypy_convert(cpy_operator.sub(self, other))

    def __truediv__(self, other):
        return self._maybe_pypy_convert(cpy_operator.truediv(self, other))

    def __xor__(self, other):
        return self._maybe_pypy_convert(cpy_operator.xor(self, other))



    def __repr__(self):
        py_str = ffi.gc(lib.PyObject_Repr(self._cpyobj), lib.Py_DECREF)
        return pypy_convert(py_str)

    def __str__(self):
        py_str = ffi.gc(lib.PyObject_Str(self._cpyobj), lib.Py_DECREF)
        return pypy_convert(py_str)

    def __dir__(self):
        py_lst = ffi.gc(lib.PyObject_Dir(self._cpyobj), lib.Py_DECREF)
        return pypy_convert(py_lst)

    def __getattr__(self, name):
        return self._getattr(name)

    def _getattr(self, name):
        c_name = ffi.new("char[]", name)
        py_attr = ffi.gc(
                lib.PyObject_GetAttrString(self._cpyobj, c_name),
                lib.Py_DECREF)
        return self._maybe_pypy_convert(py_attr)

    def __setattr__(self, key, value):
        lib.PyObject_SetAttr(self._cpyobj, convert(key), convert(value))

    def __getitem__(self, key):
        py_res = ffi.gc(
                lib.PyObject_GetItem(self._cpyobj, convert(key)),
                lib.Py_DECREF)
        return self._maybe_pypy_convert(py_res)

    def __setitem__(self, key, value):
        lib.PyObject_SetItem(self._cpyobj, convert(key), convert(value))

    def __delitem__(self, key):
        lib.PyObject_DelItem(self._cpyobj, convert(key))

    def __len__(self):
        return lib.PyObject_Size(self._cpyobj)

    def __nonzero__(self):
        return lib.PyObject_IsTrue(self._cpyobj) == 1

    def __iter__(self):
        py_iter = ffi.gc(lib.PyObject_GetIter(self._cpyobj), lib.Py_DECREF)
        while True:
            py_next = lib.PyIter_Next(py_iter)
            if py_next is None:
                break
            yield self._maybe_pypy_convert(py_next)

    def __instancecheck__(self, instance):
        if type(instance) is MetabiosisWrapper:
            return self._getattr('__instancecheck__')(instance)
        else:
            return super(MetabiosisWrapper, self).__instancecheck__(instance)

    def __subclasscheck__(self, subclass):
        if type(subclass) is MetabiosisWrapper:
            return self._getattr('__subclasscheck__')(subclass)
        else:
            return super(MetabiosisWrapper, self).__subclasscheck__(subclass)

    def __call__(self, *args, **kwargs):
        return self._call(args, kwargs)

    def _call(self, args, kwargs=None, args_kwargs_converted=False):
        convert = not args_kwargs_converted
        arguments_tuple = convert_tuple(args, convert_items=convert)

        keywordargs = ffi.NULL
        if kwargs:
            keywordargs = convert_dict(kwargs, convert_values=convert)

        return_value = ffi.gc(
                lib.PyObject_Call(self._cpyobj, arguments_tuple, keywordargs),
                lib.Py_DECREF)

        return self._maybe_pypy_convert(return_value)

    def get_type(self):
        typeobject = ffi.cast("PyObject*", self._cpyobj.ob_type)

        lib.Py_INCREF(typeobject)

        return MetabiosisWrapper(ffi.gc(typeobject, lib.Py_DECREF))

    def _maybe_pypy_convert(self, py_obj):
        if isinstance(py_obj, MetabiosisWrapper):
            return py_obj
        if self._noconvert:
            return MetabiosisWrapper(py_obj, self._noconvert)
        else:
            return pypy_convert(py_obj)


def pypy_convert(obj):
    if isinstance(obj, MetabiosisWrapper):
        return obj
    type = MetabiosisWrapper(obj).get_type()._cpyobj
    if type in cpy_to_pypy_converters:
        try:
            return cpy_to_pypy_converters[type](obj)
        except NoConvertError:
            pass
    if type == ApplevelWrapped._cpyobj:
        return _obj_by_applevel[obj]
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

def pypy_convert_type(obj):
    try:
        return cpy_to_pypy_types[obj]
    except KeyError:
        raise NoConvertError

class NoConvertError(Exception):
    pass


pypy_to_cpy_converters = {
    MetabiosisWrapper : operator.attrgetter("_cpyobj"),
    int : convert_int,
    float : convert_float,
    str : convert_string,
    unicode : convert_unicode,
    tuple : convert_tuple,
    dict : convert_dict,
    list : convert_list,
    slice : convert_slice,
    bool : convert_bool,
    types.NoneType: convert_None,
    type : convert_type,
    types.FunctionType: convert_function,
    types.MethodType: convert_function,
}
pypy_to_cpy_types = {}
cpy_to_pypy_converters = {}
cpy_to_pypy_types = {}


def init_cpy_to_pypy_converters():
    global cpy_to_pypy_converters

    import __builtin__
    builtin = pymetabiosis.module.import_module("__builtin__", noconvert=True)
    types = pymetabiosis.module.import_module("types")

    global cpy_operator
    cpy_operator = pymetabiosis.import_module('operator', noconvert=True)

    cpy_to_pypy_converters = {
            builtin.int._cpyobj : pypy_convert_int,
            builtin.float._cpyobj : pypy_convert_float,
            builtin.str._cpyobj : pypy_convert_string,
            builtin.unicode._cpyobj : pypy_convert_unicode,
            builtin.tuple._cpyobj : pypy_convert_tuple,
            builtin.dict._cpyobj : pypy_convert_dict,
            builtin.list._cpyobj : pypy_convert_list,
            builtin.bool._cpyobj : pypy_convert_bool,
            builtin.type._cpyobj : pypy_convert_type,
            types.NoneType._cpyobj : pypy_convert_None,
            }

    converted_types = ['int', 'float', 'bool', 'str', 'unicode']
    for _type in converted_types:
        cpy_type = getattr(builtin, _type)._cpyobj
        pypy_type = getattr(__builtin__, _type)
        cpy_to_pypy_types[cpy_type] = pypy_type
        pypy_to_cpy_types[pypy_type] = cpy_type


def applevel(code, noconvert=False):
    code = '\n'.join(['    ' + line for line in code.split('\n') if line])
    code = 'def anonymous():\n' + code
    py_code = ffi.gc(
            lib.Py_CompileString(code, 'exec', lib.Py_file_input),
            lib.Py_DECREF)
    lib.Py_INCREF(py_code)
    py_elem = lib.PyObject_GetAttrString(py_code, 'co_consts')
    lib.Py_INCREF(py_elem)
    py_zero = ffi.gc(lib.PyInt_FromLong(0), lib.Py_DECREF)
    py_item = lib.PyObject_GetItem(py_elem, py_zero)
    py_locals = ffi.gc(lib.PyDict_New(), lib.Py_DECREF)
    py_globals = ffi.gc(lib.PyDict_New(), lib.Py_DECREF)
    py_bltns = lib.PyEval_GetBuiltins()
    lib.PyDict_SetItemString(py_globals, '__builtins__', py_bltns)
    py_res = lib.PyEval_EvalCode(py_item, py_globals, py_locals)
    return MetabiosisWrapper(py_res, noconvert=noconvert)

ApplevelWrapped = applevel('''
class ApplevelWrapped(object):
    pass
return ApplevelWrapped
''', noconvert=True)

_applevel_by_obj = {}
_applevel_by_unhashable_obj = identity_dict()
_obj_by_applevel = {}

def convert_unknown(obj):
    try:
        aw = _applevel_by_obj.get(obj)
    except TypeError:
        aw = _applevel_by_unhashable_obj.get(obj)
    if aw is None:
        aw = ApplevelWrapped()._cpyobj
        try:
            _applevel_by_obj[obj] = aw
        except TypeError:
            _applevel_by_unhashable_obj[obj] = aw
        _obj_by_applevel[aw] = obj
    lib.Py_INCREF(aw)
    return aw
