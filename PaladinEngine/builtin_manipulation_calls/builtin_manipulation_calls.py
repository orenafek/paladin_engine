import functools
from copy import copy
from dataclasses import dataclass
from typing import Type, Callable, Any, Dict

__BUILTIN_COLLECTIONS__ = {list, set, tuple}

__BUILTIN_COLLECTIONS_MANIPULATION_METHODS__ = {
    list: [list.append, list.remove, list.extend, list.reverse, list.clear, list.__setitem__],
    set: [set.add, set.remove, set.clear, set.update, set.difference_update, set.discard,
          set.intersection_update, set.symmetric_difference_update],
    dict: [dict.__setitem__, dict.clear, dict.update]
}

EMPTY = object()


@dataclass
class Postpone(object):
    manip_name: str
    _type: Type
    value: Any

    def __hash__(self) -> int:
        return hash(id(self))


def UPDATE_DICT_OBJECT_WITH_MANIPULATION_METHOD(d: Dict, _type: Type, manip_name: str, v: Any):
    collection = _type(d.values())
    try:
        if v != EMPTY:
            collection.__getattribute__(manip_name)(v)
        else:
            collection.__getattribute__(manip_name)()
        return {(i, type(e)): e for i, e in enumerate(collection)}

    except TypeError:
        d_new = copy(d)
        d_new[(len(d.keys()), Postpone)] = Postpone(manip_name, _type, v)
        return d_new


__BUILTIN_COLLECTIONS_MANIPULATION_METHOD_NAMES__ = list(
    map(lambda f: f.__name__, functools.reduce(lambda ll, l: ll + l,
                                               __BUILTIN_COLLECTIONS_MANIPULATION_METHODS__.values(),
                                               [])))


# noinspection PyPep8Naming
def IS_SUSPECT_BUILTIN_MANIPULATION_FUNCTION_CALL(func_name: str) -> bool:
    return func_name in __BUILTIN_COLLECTIONS_MANIPULATION_METHOD_NAMES__


# noinspection PyPep8Naming
def IS_BUILTIN_MANIPULATION_FUNCTION_CALL(caller: object) -> bool:
    return any([isinstance(caller, t) for t in __BUILTIN_COLLECTIONS_MANIPULATION_METHODS__])


def IS_BUILTIN_MANIPULATION_TYPE(t: Type) -> bool:
    return t in __BUILTIN_COLLECTIONS__


# noinspection PyTypeChecker
def MANIPULATION_BY_OBJ_TYPE_AND_FUNC_NAME(t: Type, func_name: str) -> Callable:
    return [m.__name__ == func_name for m in __BUILTIN_COLLECTIONS_MANIPULATION_METHODS__[t]][0]


def CREATE_POSTPONED_DICT_OBJECT_WITH_MANIPULATION_METHOD(obj: Dict, builtin_type: Type,
                                                          manipulation_function_name: str,
                                                          value: Any):
    d_new = copy(obj)
    d_new[(len(obj.keys()), Postpone)] = Postpone(manipulation_function_name, builtin_type, value)
    return d_new
