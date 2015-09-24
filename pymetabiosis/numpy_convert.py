from pymetabiosis.module import import_module
from pymetabiosis.wrapper import MetabiosisWrapper, cpy_to_pypy_converters


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
