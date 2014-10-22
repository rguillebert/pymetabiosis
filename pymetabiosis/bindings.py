import atexit
from cffi import FFI

ffi = FFI()

ffi.cdef("""
         typedef ... PyTypeObject;

         typedef struct {
             PyTypeObject* ob_type;
             ...;
         } PyObject;

         typedef size_t Py_ssize_t;

         void Py_Initialize();
         void Py_Finalize();

         int PyRun_SimpleString(const char *command);

         void Py_INCREF(PyObject *o);
         void Py_XINCREF(PyObject *o);
         void Py_DECREF(PyObject *o);
         void Py_XDECREF(PyObject *o);

         // Importing: https://docs.python.org/2/c-api/import.html
         PyObject* PyImport_ImportModule(const char *name);

         // Exceptions: https://docs.python.org/2/c-api/exceptions.html
         PyObject* PyErr_Occurred();
         void PyErr_Print();
         void PyErr_Clear();
         int PyErr_ExceptionMatches(PyObject *exc);
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
         PyObject* PyObject_Call(PyObject *callable_object, PyObject *args, PyObject *kw);
         PyObject* PyObject_GetAttrString(PyObject *o, const char *attr_name);

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
         PyObject* PyDict_Items(PyObject *p);

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
                 """, libraries=["python2.7"], flags=ffi.RTLD_GLOBAL)

lib.Py_Initialize()
atexit.register(lib.Py_Finalize)


def add_exception_handling(name, errcond=ffi.NULL):

    fn = getattr(lib, name)

    def wrapper(*args):
        res = fn(*args)
        if errcond == res:
            py_exc_type = lib.PyErr_Occurred()
            if py_exc_type is None:
                # Some functions return NULL without raising an exception,
                # but also can raise an exception
                # (and also return NULL in this case).
                return None
            if py_exc_type in exception_by_py_exc:
                lib.PyErr_Print()
                # TODO - get value
                raise exception_by_py_exc[py_exc_type]
            # less generic types first
            for py_exc_type, exc_type in reversed(exceptions):
                if lib.PyErr_ExceptionMatches(py_exc_type):
                    lib.PyErr_Print()
                    # TODO - get value
                    raise exc_type
            lib.PyErr_Print()
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
        ]:
    if not isinstance(args, tuple):
        args = (args,)
    add_exception_handling(*args)
