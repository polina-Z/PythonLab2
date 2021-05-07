import builtins
import types
import logging


logging.basicConfig(
    level=logging.WARNING, filename="warning.log", format="%(levelname)s: %(message)s"
)

dumped = []

funcattrs = (
    "__name__",
    "__qualname__",
    "__doc__",
    "__dict__",
    "__module__",
    "__closure__",
    "__defaults__",
    "__kwdefaults__",
    "__annotations__",
    "__code__",
)

codeattrs = (
    "co_argcount",
    "co_posonlyargcount",
    "co_kwonlyargcount",
    "co_nlocals",
    "co_stacksize",
    "co_flags",
    "co_code",
    "co_consts",
    "co_names",
    "co_varnames",
    "co_filename",
    "co_name",
    "co_firstlineno",
    "co_lnotab",
    "co_freevars",
    "co_cellvars",
)

moduleattrs = ("__name__", "__doc__")

builtin = (
    *(
        getattr(builtins, key)
        for key in dir(builtins)
        if type(getattr(builtins, key)) is type
    ),
    *(getattr(types, key) for key in dir(types) if type(getattr(types, key)) is type),
)


def dump_as_is(obj):
    return obj


def dump_tuple(tuple_obj):
    tmp = []
    for obj in tuple_obj:
        try:
            tmp.append(dump_obj(obj))
        except TypeError as error:
            logging.warning(f"<{_dump_hint(obj)}> was skipped because of {error}")
    return tmp


def dump_id(obj):
    return hex(id(obj))


def dump_hint(obj):
    if hasattr(obj, "__name__"):
        string = "'" + obj.__name__ + "'"
    else:
        string = "instance"
    string += " of '" + type(obj).__name__
    string += "' at " + dump_id(obj)
    return string


def dump_simple(obj):
    dumped.append(id(obj))
    return {
        "__id__": dump_id(obj),
        "__class__": dump_obj(type(obj)),
    }


def dump_value(obj, value):
    dict_to_dump = dump_simple(obj)
    dict_to_dump["__value__"] = dump_obj(value)
    return dict_to_dump


def dump_specattrs(obj, specattrs):
    dict_to_dump = dump_simple(obj)
    for attr in specattrs:
        dict_to_dump[attr] = dump_obj(getattr(obj, attr))
    return dict_to_dump


def dump_func(func):
    def dump_globals(code):
        glob.extend(code.co_names)
        for const in code.co_consts:
            if type(const) is types.CodeType:
                dump_globals(const)

    glob = []
    dump_globals(func.__code__)
    glob_dct = {var: func.__globals__[var] for var in func.__globals__ if var in glob}
    return {**dump_specattrs(func, funcattrs), "__globals__": dump_obj(glob_dct)}


def dump_custom(obj):
    dict_to_dump = dump_simple(obj)
    dict_to_dump["__name__"] = dump_obj(getattr(obj, "__name__"))
    dict_to_dump["__bases__"] = dump_obj(getattr(obj, "__bases__"))
    dict_to_dump["__dict__"] = dump_obj(getattr(obj, "__dict__"))
    return dict_to_dump


supported = {
    type(None): dump_as_is,
    bool: dump_as_is,
    type: dump_custom,
    object: dump_simple,
    int: dump_as_is,
    float: dump_as_is,
    complex: lambda obj: dump_value(obj, (obj.real, obj.imag)),
    str: dump_as_is,
    list: lambda obj: dump_value(obj, tuple(obj)),
    tuple: dump_tuple,
    range: lambda obj: dump_value(obj, (obj.start, obj.stop, obj.step)),
    bytes: lambda obj: dump_value(obj, obj.hex(" ", 1)),
    bytearray: lambda obj: dump_value(obj, obj.hex(" ", 1)),
    memoryview: lambda obj: dump_value(obj, obj.obj),
    set: lambda obj: dump_value(obj, tuple(obj)),
    frozenset: lambda obj: dump_value(obj, tuple(obj)),
    dict: lambda obj: dump_value(obj, tuple(obj.items())),
    types.MappingProxyType: lambda obj: dump_value(obj, tuple(obj.items())),
    types.FunctionType: lambda obj: dump_func(obj),
    types.CodeType: lambda obj: dump_specattrs(obj, codeattrs),
    types.CellType: lambda obj: dump_value(obj, obj.cell_contents),
    types.ModuleType: lambda obj: dump_specattrs(obj, moduleattrs),
}

unsupported = tuple(cls for cls in builtin if cls not in supported)


def dump_obj(obj):
    if obj in builtin:
        return {"__id__": str(obj)}
    if id(obj) in dumped:
        return {"__id__": dump_hint(obj)}
    if type(obj) in unsupported:
        raise TypeError(f"<{dump_hint(obj)}> has unsupported type")
    return supported.get(type(obj), dump_custom)(obj)


def dump(obj):
    dumped.clear()
    return dump_obj(obj)
