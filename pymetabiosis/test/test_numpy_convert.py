import pytest
from pymetabiosis.module import import_module
from pymetabiosis.numpy_convert import \
        register_cpy_numpy_to_pypy_builtin_converters, \
        register_pypy_cpy_ndarray_converters


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


def test_pypy_ndarray_converter():
    np = _import_pypy_numpy()
    cpython_numpy = _import_cpy_numpy()
    builtin = import_module("__builtin__", noconvert=True)
    operator = import_module("operator", noconvert=True)
    register_pypy_cpy_ndarray_converters()
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
    m1 = np.array([[1, 2], [2, 3]])
    m2 = np.array([[3, 1], [-2, 4]])
    cpython_numpy.add(m1, m2, out=m1)
    assert type(m1) is np.ndarray
    assert m1[1][1] == 7
    # convert from CPython ndarray to PyPy ndarray
    m3 = cpython_numpy.add(m1, m2)
    assert type(m3) is np.ndarray
    assert m3.dtype is m1.dtype
    assert m3[1][1] == 11
    a = np.random.random(30) + 1j*np.random.rand(30)
    x = cpython_numpy.fft.fft(a)
    assert type(x) is np.ndarray
    assert x.shape == (30,)

def test_pypy_ndarray_offset_handling():
    np = _import_pypy_numpy()
    cpython_numpy = _import_cpy_numpy()
    register_pypy_cpy_ndarray_converters()
    x = np.asarray((complex(1, 2), complex(3, 4)))
    assert cpython_numpy.sum(x.real) == 4.0
    assert cpython_numpy.sum(x.imag) == 6.0

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
