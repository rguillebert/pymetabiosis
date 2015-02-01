PyMetabiosis
============

A bridge between PyPy and CPython that works by embedding CPython, its main purpose it to allow you to use any CPython module on PyPy (including C extensions).

* PyMetabiosis tries to link with the python command available on $PATH, however you can override this (if you want to use a virtualenv and/or if "python" points to PyPy) by setting the PYTHON_EMBED environment variable to a virtualenv

* Use pymetabiosis.module.import_module to import cpython modules on PyPy
