from pymetabiosis import import_module

builtin = import_module("__builtin__")

def activate_virtualenv(path):
    builtin.execfile(path, {"__file__" : path})
