import pytest
from pymetabiosis.module import import_module
from pymetabiosis.numpy_convert import \
        register_cpy_numpy_to_pypy_builtin_converters, \
        register_pypy_cpy_numpy_converters


def test_scalar_converter():
    numpy = _import_cpy_numpy()
    register_cpy_numpy_to_pypy_builtin_converters()

    assert numpy.bool_(True) is True
    assert numpy.bool_(False) is False

    assert numpy.int8(10) == 10
    assert numpy.int16(-10) == -10
    assert numpy.int32(int(2**31-1)).__int__() == int(2**31-1)
    assert numpy.int64(42) == 42

    assert numpy.float16(10.0) == 10.0
    assert numpy.float32(-10) == -10.0
    assert numpy.float64(42.0) == 42.0
    if hasattr(numpy, "float128"):
        assert numpy.float128(-42.0) == -42.0


def test_pypy_numpy_converter():
    np = _import_pypy_numpy()
    cpython_numpy = _import_cpy_numpy()
    builtin = import_module("__builtin__", noconvert=True)
    operator = import_module("operator", noconvert=True)
    register_pypy_cpy_numpy_converters()
    arr = np.zeros(2) + 1
    assert cpython_numpy.sum(arr) == 2.0
    arr = np.array([2, 3], dtype=np.int8)
    assert cpython_numpy.sum(arr) == 5
    for dtype in [
            np.int8, np.uint8, np.int16, np.uint16, np.int32, np.uint32,
            np.int64, np.uint64,
            np.float16, np.float32, np.float64]:
        m = np.zeros((17, 13), dtype=dtype)
        assert builtin.len(m) == 17
        assert operator.attrgetter('dtype.name')(m) == dtype.__name__
        assert operator.attrgetter('shape')(m) == (17, 13)
    # TODO - returning from cpython_numpy
   #cpython_numpy.add(m1, m2, out=m1)
   #assert m1[1][1] == 3


def _import_pypy_numpy():
    try:
        import numpy
    except ImportError:
        pytest.skip("numpy isn't installed on pypy side")
    else:
        return numpy


def _import_cpy_numpy():
    try:
        return import_module("numpy")
    except ImportError:
        pytest.skip("numpy isn't installed on the cpython side")
