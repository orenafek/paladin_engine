import functools
from collections import deque
from copy import copy
from dataclasses import dataclass
from typing import Type, Any, Dict, Tuple

__BUILTIN_COLLECTIONS__ = {list, set, tuple, deque}

EMPTY = object()
EMPTY_COLLECTION = object()


@dataclass
class Postpone(object):
    manip_name: str
    builtin_type: Type
    arg_type: Type
    arg_value: Any

    def __hash__(self) -> int:
        return hash(id(self))


class BuiltinCollectionsUtils(object):
    _BUILTIN_COLLECTIONS_METHODS_MAPPING = {
        list: [list.append, list.remove, list.extend, list.reverse, list.clear, list.__setitem__, list.pop],
        set: [set.add, set.remove, set.clear, set.update, set.difference_update, set.discard,
              set.intersection_update, set.symmetric_difference_update],
        dict: [dict.__setitem__, dict.clear, dict.update],
        deque: [deque.append, deque.appendleft, deque.remove, deque.extend, deque.extendleft, deque.reverse, deque.clear,
                deque.pop, deque.popleft, deque.__setitem__]
    }

    _BUILTIN_COLLECTIONS_METHOD_NAMES = list(
        map(lambda f: f.__name__,
            functools.reduce(lambda ll, l: ll + l, _BUILTIN_COLLECTIONS_METHODS_MAPPING.values(), [])))

    @staticmethod
    def is_builtin_collection_type(t: Type) -> bool:
        return t in __BUILTIN_COLLECTIONS__

    @staticmethod
    def is_builtin_collection(i: Any) -> bool:
        return any([isinstance(i, t) for t in __BUILTIN_COLLECTIONS__])

    @staticmethod
    def update_dict_object_with_builtin_method(d: Dict, col_type: Type, manip_name: str, v: Any) -> Dict[
        Tuple[int, Type], Any]:
        collection = col_type(d.values())
        if v != EMPTY:
            collection.__getattribute__(manip_name)(v)
        else:
            collection.__getattribute__(manip_name)()
        return {(type(e), i): e for i, e in enumerate(collection)}

    @staticmethod
    def is_function_suspicious_as_builtin_collection_method(func_name: str) -> bool:
        return func_name in BuiltinCollectionsUtils._BUILTIN_COLLECTIONS_METHOD_NAMES

    @staticmethod
    def is_builtin_collection_method(caller: object) -> bool:
        return any([isinstance(caller, t) for t in BuiltinCollectionsUtils._BUILTIN_COLLECTIONS_METHODS_MAPPING])

    @staticmethod
    def create_dict_object_with_postponed_builtin_collection_methods(obj: Dict, builtin_type: Type,
                                                                     manipulation_function_name: str,
                                                                     arg_type: Type,
                                                                     arg_value: Any):
        d_new = copy(obj)
        d_new[(Postpone, len(obj.keys()))] = Postpone(manipulation_function_name, builtin_type, arg_type, arg_value)
        return d_new
