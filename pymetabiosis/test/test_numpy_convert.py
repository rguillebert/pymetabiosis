from pymetabiosis.module import import_module
from pymetabiosis.numpy_convert import \
        register_cpy_numpy_to_pypy_builin_converters

register_cpy_numpy_to_pypy_builin_converters()

def test_scalar_converter():
    numpy = import_module("numpy")

    assert numpy.bool_(True) is True
    assert numpy.bool_(False) is False

    assert numpy.int8(10) == 10
    assert numpy.int16(-10) == -10
    assert numpy.int32(2**31-1) == 2**31-1
    assert numpy.int64(42) == 42

    assert numpy.float16(10.0) == 10.0
    assert numpy.float32(-10) == -10.0
    assert numpy.float64(42.0) == 42.0
    assert numpy.float128(-42.0) == -42.0

