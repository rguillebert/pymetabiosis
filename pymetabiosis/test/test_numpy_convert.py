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
    pypy_numpy = _import_pypy_numpy()
    cpython_numpy = _import_cpy_numpy()
    register_pypy_cpy_numpy_converters()
    arr = pypy_numpy.zeros(2) + 1
    assert cpython_numpy.sum(arr) == 2.0
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
