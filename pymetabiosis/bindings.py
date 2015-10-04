import atexit
from cffi import FFI
import os
from subprocess import check_output
import sys


def _get_python():
    """Find a suitable Python to embed.
    """
    python_embed_prefix = os.environ.get('PYTHON_EMBED', '')
    if not python_embed_prefix:
        python = check_output(
            ["python", "-c", "import sys;print sys.executable"]
        ).strip()
    else:
        if sys.platform == 'win32':
            python = os.path.join(python_embed_prefix, 'python.exe')
        else:
            python = os.path.join(python_embed_prefix, 'bin', 'python')
    advice = "Please set your PYTHON_EMBED env var to point to your Python "\
             "installation."
    if not os.path.exists(python):
        raise RuntimeError("Can not find python at %s. %s" % (python, advice))
    is_pypy = check_output(
        [python, "-c", "import sys;print hasattr(sys, 'pypy_version_info')"]
    ).strip()
    if is_pypy.lower() == "true":
        msg = "%s is a PyPy interpreter and not Python. %s" % (python, advice)
        raise RuntimeError(msg)
    return python

PYTHON = _get_python()

def _get_include_dirs():
    return [check_output(
        [PYTHON, "-c",
         "from distutils import sysconfig;"
         "print sysconfig.get_python_inc()"]
    ).strip()]


def _get_library_dirs():
    return [check_output(
        [PYTHON, "-c",
         "from distutils import sysconfig;"
         "print sysconfig.get_config_var('LIBDIR')"]
    ).strip()]

LIBDIRS = _get_library_dirs()

def _get_extra_link_args():
    args = []
    if sys.platform == 'darwin':
        libdir = LIBDIRS[0]
        args.append("-Wl,-rpath,%s"%os.path.dirname(libdir))
    elif sys.platform.startswith("linux"):
        libdir = LIBDIRS[0]
        args.append("-Wl,-rpath,%s"%libdir)

    return args


ffi = FFI()

ffi.cdef("""
         typedef ... PyTypeObject;

         typedef size_t Py_ssize_t;

         typedef struct {
             PyTypeObject* ob_type;
             Py_ssize_t ob_refcnt;
             ...;
         } PyObject;

         void Py_Initialize();
         void Py_Finalize();

         void Py_SetProgramName(char *name);
         int PyRun_SimpleString(const char *command);

         void Py_INCREF(PyObject *o);
         void Py_XINCREF(PyObject *o);
         void Py_DECREF(PyObject *o);
         void Py_XDECREF(PyObject *o);

         const int Py_file_input;
         PyObject* Py_CompileString(const char *str, const char *filename, int start);
         PyObject* PyEval_GetBuiltins();
         PyObject* PyEval_EvalCode(PyObject *co, PyObject *globals, PyObject *locals);

         // Importing: https://docs.python.org/2/c-api/import.html
         PyObject* PyImport_ImportModule(const char *name);

         // Exceptions: https://docs.python.org/2/c-api/exceptions.html
         PyObject* PyErr_Occurred();
         void PyErr_Print();
         void PyErr_Clear();
         int PyErr_ExceptionMatches(PyObject *exc);
         void PyErr_SetString(PyObject *type, const char *message);
         PyObject* const PyExc_BaseException;
         PyObject* const PyExc_Exception;
         PyObject* const PyExc_StandardError;
         PyObject* const PyExc_ArithmeticError;
         PyObject* const PyExc_LookupError;
         PyObject* const PyExc_AssertionError;
         PyObject* const PyExc_AttributeError;
         PyObject* const PyExc_EOFError;
         PyObject* const PyExc_EnvironmentError;
         PyObject* const PyExc_FloatingPointError;
         PyObject* const PyExc_IOError;
         PyObject* const PyExc_ImportError;
         PyObject* const PyExc_IndexError;
         PyObject* const PyExc_KeyError;
         PyObject* const PyExc_KeyboardInterrupt;
         PyObject* const PyExc_MemoryError;
         PyObject* const PyExc_NameError;
         PyObject* const PyExc_NotImplementedError;
         PyObject* const PyExc_OSError;
         PyObject* const PyExc_OverflowError;
         PyObject* const PyExc_ReferenceError;
         PyObject* const PyExc_RuntimeError;
         PyObject* const PyExc_SyntaxError;
         PyObject* const PyExc_SystemError;
         PyObject* const PyExc_SystemExit;
         PyObject* const PyExc_TypeError;
         PyObject* const PyExc_ValueError;
         PyObject* const PyExc_ZeroDivisionError;

         // Object: https://docs.python.org/2/c-api/object.html
         PyObject* PyObject_Str(PyObject *o);
         PyObject* PyObject_Repr(PyObject *o);
         PyObject* PyObject_Dir(PyObject *o);
         PyObject* PyObject_Call(PyObject *callable_object, PyObject *args, PyObject *kw);
         PyObject* PyObject_GetAttrString(PyObject *o, const char *attr_name);
         PyObject* PyObject_SetAttr(PyObject *o, PyObject *attr_name, PyObject *v);
         PyObject* PyObject_GetItem(PyObject *o, PyObject *key);
         int PyObject_SetItem(PyObject *o, PyObject *key, PyObject *v);
         int PyObject_DelItem(PyObject *o, PyObject *key);
         Py_ssize_t PyObject_Size(PyObject *o);
         PyObject* PyObject_GetIter(PyObject *o);
         int PyObject_IsTrue(PyObject *o);

         // Creating CPython function that call cffi callbacks
         // https://docs.python.org/2/c-api/structures.html#c.PyCFunction
         // http://bugs.python.org/file32578/16776.txt
         int const METH_VARARGS;
         int const METH_KEYWORDS;
         typedef ... PyCFunction;
         typedef struct {
            char* ml_name; // name of the method
            void* ml_meth; // pointer to the C implementation
            int ml_flags;   // flag bits indicating how the call should be constructed
            char* ml_doc;   // points to the contents of the docstring
            ...;
         } PyMethodDef;
         PyObject* PyCFunction_New(PyMethodDef *ml, PyObject *self);

         // Iterator: https://docs.python.org/2/c-api/iter.html
         PyObject* PyIter_Next(PyObject *o);

         // String: https://docs.python.org/2/c-api/string.html
         char* PyString_AsString(PyObject *string);
         PyObject* PyString_FromString(const char *v);

         // Unicode: https://docs.python.org/2/c-api/unicode.html
         PyObject* PyUnicode_AsUTF8String(PyObject* obj);
         PyObject* PyUnicode_FromString(const char *u);

         // Tuple: https://docs.python.org/2/c-api/tuple.html
         PyObject* PyTuple_Pack(Py_ssize_t n, ...);
         PyObject* PyTuple_GetItem(PyObject* tuple, int index);
         Py_ssize_t PyTuple_Size(PyObject* obj);

         // List: https://docs.python.org/2/c-api/list.html
         PyObject* PyList_New(Py_ssize_t len);
         PyObject* PyList_GetItem(PyObject *list, Py_ssize_t index);
         Py_ssize_t PyList_Size(PyObject *list);
         int PyList_SetItem(PyObject *list, Py_ssize_t index, PyObject *item);

         // Dict: https://docs.python.org/2/c-api/dict.html
         PyObject* PyDict_New();
         int PyDict_SetItem(PyObject *p, PyObject *key, PyObject *val);
         int PyDict_SetItemString(PyObject *p, const char *key, PyObject *val);
         PyObject* PyDict_Items(PyObject *p);

         // Slice: https://docs.python.org/2/c-api/slice.html
         PyObject* PySlice_New(PyObject *start, PyObject *stop, PyObject *step);

         // Integer: http://docs.python.org/2/c-api/int.html
         PyObject* PyInt_FromLong(long ival);
         long PyLong_AsLong(PyObject *obj);

         // Boolean: https://docs.python.org/2/c-api/bool.html
         PyObject* const Py_False;
         PyObject* const Py_True;

         PyObject* const Py_None;

         // Float: https://docs.python.org/2/c-api/float.html
         PyObject* PyFloat_FromDouble(double dval);
         double PyFloat_AsDouble(PyObject *obj);

         """)

lib = ffi.verify("""
                 #include<Python.h>
                 #ifdef PyTuple_GetItem
                 #error "Picking Python.h from pypy"
                 #endif
                 """,
                 include_dirs=_get_include_dirs(),
                 libraries=["python2.7"],
                 library_dirs=LIBDIRS,
                 extra_link_args=_get_extra_link_args(),
                 flags=ffi.RTLD_GLOBAL)

prog_name = ffi.new("char[]", PYTHON)
lib.Py_SetProgramName(prog_name)
lib.Py_Initialize()
atexit.register(lib.Py_Finalize)


def add_exception_handling(name, errcond=ffi.NULL):

    fn = getattr(lib, name)

    def wrapper(*args):
        res = fn(*args)
        if errcond == res:
            py_exc_type = lib.PyErr_Occurred()
            if py_exc_type == ffi.NULL:
                # Some functions return NULL without raising an exception,
                # but also can raise an exception
                # (and also return NULL in this case).
                return None
            if py_exc_type in exception_by_py_exc:
                lib.PyErr_Clear()
                # TODO - get value
                raise exception_by_py_exc[py_exc_type]
            # less generic types first
            for py_exc_type, exc_type in reversed(exceptions):
                if lib.PyErr_ExceptionMatches(py_exc_type):
                    lib.PyErr_Clear()
                    # TODO - get value
                    raise exc_type
            lib.PyErr_Clear()
            raise Exception("Call of '%s' exploded" % name)
        return res

    setattr(lib, name, wrapper)


_exceptions = [
    ('PyExc_BaseException', BaseException),
    ('PyExc_Exception', Exception),
    ('PyExc_StandardError', StandardError),
    ('PyExc_ArithmeticError', ArithmeticError),
    ('PyExc_LookupError', LookupError),
    ('PyExc_AssertionError', AssertionError),
    ('PyExc_AttributeError', AttributeError),
    ('PyExc_EOFError', EOFError),
    ('PyExc_EnvironmentError', EnvironmentError),
    ('PyExc_FloatingPointError', FloatingPointError),
    ('PyExc_IOError', IOError),
    ('PyExc_ImportError', ImportError),
    ('PyExc_IndexError', IndexError),
    ('PyExc_KeyError', KeyError),
    ('PyExc_KeyboardInterrupt', KeyboardInterrupt),
    ('PyExc_MemoryError', MemoryError),
    ('PyExc_NameError', NameError),
    ('PyExc_NotImplementedError', NotImplementedError),
    ('PyExc_OSError', OSError),
    ('PyExc_OverflowError', OverflowError),
    ('PyExc_ReferenceError', ReferenceError),
    ('PyExc_RuntimeError', RuntimeError),
    ('PyExc_SyntaxError', SyntaxError),
    ('PyExc_SystemError', SystemError),
    ('PyExc_SystemExit', SystemExit),
    ('PyExc_TypeError', TypeError),
    ('PyExc_ValueError', ValueError),
   #('PyExc_WindowsError', WindowsError),
    ('PyExc_ZeroDivisionError', ZeroDivisionError),
]

exceptions = [(getattr(lib, exc_name), exc) for exc_name, exc in _exceptions]
exception_by_py_exc =  dict(exceptions)


# Add exception handling for all functions that can raise errors

for args in [
        'PyImport_ImportModule',
        'PyObject_Str',
        'PyObject_Repr',
        'PyObject_Call',
        'PyObject_GetAttrString',
        'PyObject_GetItem',
        ('PyObject_SetItem', -1),
        ('PyObject_DelItem', -1),
        ('PyObject_Size', int(ffi.cast('Py_ssize_t', -1))),
        'PyObject_GetIter',
        ('PyObject_IsTrue', -1),
        'PyIter_Next',
        'PyString_AsString',
        'PyString_FromString',
        'PyUnicode_AsUTF8String', # ? docs say nothing about these two
        'PyUnicode_FromString',
        'PyTuple_Pack',
        'PyTuple_GetItem',
        'PyList_New',
        'PyList_GetItem',
        ('PyList_SetItem', -1),
        'PyDict_New',
        ('PyDict_SetItem', -1),
        ('PyDict_SetItemString', -1),
        ('PyLong_AsLong', -1),
        'PyFloat_FromDouble',
        ('PyFloat_FromDouble', -1.0),
        ]:
    if not isinstance(args, tuple):
        args = (args,)
    add_exception_handling(*args)
