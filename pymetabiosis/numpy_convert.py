from pymetabiosis.module import import_module
from pymetabiosis.bindings import lib, ffi
from pymetabiosis.wrapper import MetabiosisWrapper, cpy_to_pypy_converters, \
        pypy_to_cpy_converters, applevel


def register_cpy_numpy_to_pypy_builtin_converters():
    ''' Converts numpy types to builtin python types on PyPy side
    '''
    numpy = import_module("numpy")
    builtin = import_module("__builtin__", noconvert=True)
    def call_direct(f):
        f = MetabiosisWrapper(f._cpyobj, noconvert=False)
        return lambda x: f._call((x,), args_kwargs_converted=True)

    cpy_to_pypy_converters.update({
        numpy.bool_._cpyobj: call_direct(builtin.bool),
        numpy.int8._cpyobj: call_direct(builtin.int),
        numpy.int16._cpyobj: call_direct(builtin.int),
        numpy.int32._cpyobj: call_direct(builtin.int),
        numpy.int64._cpyobj: call_direct(builtin.int),
        numpy.float16._cpyobj: call_direct(builtin.float),
        numpy.float32._cpyobj: call_direct(builtin.float),
        numpy.float64._cpyobj: call_direct(builtin.float),
    })

    if hasattr(numpy, "float128"):
        cpy_to_pypy_converters.update({numpy.float128._cpyobj: call_direct(builtin.float)})


def register_pypy_cpy_ndarray_converters():
    ''' Convert numpy types from PyPy numpy to CPython numpy, and back.
    '''
    import numpy
    cpython_numpy = import_module("numpy")
    pypy_to_cpy_converters[numpy.ndarray] = convert_ndarray
    cpy_to_pypy_converters[cpython_numpy.ndarray._cpyobj] = \
        convert_from_ndarray

_convert_ndarray = applevel('''
import numpy
import ctypes
def _convert_ndarray(shape, dtype, size, strides, offset, addr):
    return numpy.ndarray(
        shape=shape,
        dtype=dtype,
        strides=strides,
        offset=offset,
        buffer=(ctypes.c_char*size).from_address(addr))
return _convert_ndarray
''', noconvert=True)

_convert_from_ndarray = applevel('''
import numpy
def _convert_from_ndarray(obj):
    base = obj.base if isinstance(obj.base, numpy.ndarray) else obj
    offset = obj.__array_interface__['data'][0] - \
             base.__array_interface__['data'][0]
    return (obj.shape,
            obj.dtype.name,
            len(base.data),
            obj.strides,
            offset,
            base.__array_interface__["data"][0])
return _convert_from_ndarray
''')

try:
    import ctypes
    import numpy
except ImportError:
    pass
else:
    def convert_ndarray(obj):
        base = obj.base if isinstance(obj.base, numpy.ndarray) else obj
        offset = obj.__array_interface__['data'][0] - \
                 base.__array_interface__['data'][0]
        w = _convert_ndarray(
            obj.shape,
            obj.dtype.name,
            len(base.data),
            obj.strides,
            offset,
            base.__array_interface__["data"][0])
        return ffi.gc(w._cpyobj, lib.Py_DECREF)

    def convert_from_ndarray(obj):
        shape, dtype, size, strides, offset, addr = _convert_from_ndarray\
            ._call((obj,), args_kwargs_converted=True)
        return numpy.ndarray(
            shape=shape,
            dtype=dtype,
            strides=strides,
            offset=offset,
            buffer=(ctypes.c_char*size).from_address(addr))
