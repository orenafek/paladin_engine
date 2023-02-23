import functools
from typing import Type, Union, List, Set, Dict, Callable

__BUILTIN_COLLECTIONS__ = {list, set, dict}

__BUILTIN_COLLECTIONS_MANIPULATION_METHODS__ = {
    list: [list.append, list.remove, list.extend, list.reverse, list.clear, list.__setitem__],
    set: [set.add, set.remove, set.clear, set.update],
    dict: [dict.__setitem__, dict.clear, dict.update]
}

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


# noinspection PyTypeChecker
def MAINPULATION_BY_OBJ_TYPE_AND_FUNC_NAME(t: Type, func_name: str) -> Callable:
    return [m.__name__ == func_name for m in __BUILTIN_COLLECTIONS_MANIPULATION_METHODS__[t]][0]
