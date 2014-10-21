from cffi import FFI
import sys

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

         PyObject* PyImport_ImportModule(const char *name);
         PyObject* PyErr_Occurred();
         void PyErr_Print();

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

         // Float: https://docs.python.org/2/c-api/float.html
         PyObject* PyFloat_FromDouble(double dval);
         double PyFloat_AsDouble(PyObject *obj);

         """)

lib = ffi.verify("""
                 #include<Python.h>
                 """, libraries=["python2.7"], flags=ffi.RTLD_GLOBAL)

lib.Py_Initialize()
