from functools import wraps
from time import time
from types import NoneType
from typing import Any, Union, Iterable, Callable

__PRIMITIVES = [int, float, str, bool, complex, NoneType]


def ISP(t: type) -> bool:
    return t in __PRIMITIVES


def POID(v: Any) -> Union[Union[int, float, str, bool, complex], int]:
    return v if ISP(type(v)) else id(v)


def IS_ITERABLE(i: Union[Iterable, object]):
    try:
        _ = iter(i)
        return True
    except TypeError:
        return False


def ISFOM(t: type) -> bool:
    return issubclass(t, Callable)


PALADIN_OBJECT_COLLECTION_FIELD = '__PALADIN_INIT_COLLECT__'
PALADIN_OBJECT_COLLECTION_EXPRESSION = '__PALADIN_INIT_COLLECT_EXPRESSION__'


def TIME(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time()
        ret = f(*args, **kwargs)
        end_time = time()
        print(f'{f.__name__}: {10 ** 3 * (end_time - start_time)}msec')
        return ret

    return wrapper
