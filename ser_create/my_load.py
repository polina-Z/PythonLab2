import builtins
import inspect
import types
from importlib import import_module

loaded = {}
func_glob = {}

moduleattrs = ("__name__", "__doc__")

funcattrs_construct = (
    "__code__",
    "__globals__",
    "__name__",
    "__defaults__",
    "__closure__",
)

funcattrs_rest = (
    "__qualname__",
    "__doc__",
    "__dict__",
    "__module__",
    "__kwdefaults__",
    "__annotations__",
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

builtin = {
    **{
        str(getattr(builtins, key)): getattr(builtins, key)
        for key in dir(builtins)
        if type(getattr(builtins, key)) is type
    },
    **{
        str(getattr(types, key)): getattr(types, key)
        for key in dir(types)
        if type(getattr(types, key)) is type
    },
}


def load_id(id_str):
    return int(id_str.rpartition(" at ")[2], 0)


def load_id_data(id_str):
    if id_str.startswith("<"):
        return (builtin[id_str], True)
    else:
        id_int = load_id(id_str)
        return loaded.get(id_int, (id_int, False))


def load_dict(dct):
    return {load_obj(pair[0]): load_obj(pair[1]) for pair in dct["__value__"]}


def load_func(dct):
    tmp_dct = {key: load_obj(dct[key]) for key in funcattrs_construct}
    func_glob.update(tmp_dct["__globals__"])
    tmp_dct["__globals__"] = func_glob

    func = types.FunctionType(*tmp_dct.values())
    for key in funcattrs_rest:
        setattr(func, key, load_obj(dct[key]))

    return func


supported = {
    object: lambda dct: object(),
    complex: lambda dct: complex(*dct["__value__"]),
    list: lambda dct: list(dct["__value__"]),
    range: lambda dct: range(*dct["__value__"]),
    bytes: lambda dct: bytes.fromhex(dct["__value__"]),
    bytearray: lambda dct: bytearray.fromhex(dct["__value__"]),
    memoryview: lambda dct: memoryview(load_obj(dct["__value__"])),
    set: lambda dct: set(dct["__value__"]),
    frozenset: lambda dct: frozenset(dct["__value__"]),
    dict: load_dict,
    types.MappingProxyType: lambda dct: types.MappingProxyType(load_dict(dct)),
    types.FunctionType: load_func,
    types.CodeType: lambda dct: types.CodeType(
        *(load_obj(dct[key]) for key in codeattrs)
    ),
    types.CellType: lambda dct: types.CellType(load_obj(dct["__value__"])),
    types.ModuleType: lambda dct: import_module(dct["__name__"]),
}


def load_obj(obj2load):
    if type(obj2load) is list:
        return tuple(load_obj(element) for element in obj2load)

    if not type(obj2load) is dict:
        return obj2load

    tmp_obj, is_loaded = load_id_data(obj2load["__id__"])
    if is_loaded:
        return tmp_obj

    cls = load_obj(obj2load["__class__"])

    if "__bases__" in obj2load:
        bases = load_obj(obj2load["__bases__"])
        obj = cls(obj2load["__name__"], bases, {})
    elif cls in supported:
        obj = supported[cls](obj2load)
    else:
        obj = cls()

    loaded[tmp_obj] = (obj, True)

    if "__dict__" in obj2load:
        for key, value in load_obj(obj2load["__dict__"]).items():
            setattr(obj, key, value)
    return obj


def load(obj2load, globs={}):
    func_glob.clear()
    func_glob.update(globs)
    loaded.clear()
    return load_obj(obj2load)
