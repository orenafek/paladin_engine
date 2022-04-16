from typing import Any, Union, Iterable

__PRIMITIVES = [int, float, str, bool, complex]


def ISP(t: type) -> bool:
    return t in __PRIMITIVES


def POID(v: Any) -> Union[Union[int, float, str, bool, complex], int]:
    return v if ISP(type(v)) or type(v) is list else id(v)


def IS_ITERABLE(i: Union[Iterable, object]):
    try:
        _ = iter(i)
        return True
    except TypeError:
        return False


PALADIN_OBJECT_COLLECTION_FIELD = '__PALADIN_INIT_COLLECT__'
PALADIN_OBJECT_COLLECTION_EXPRESSION = '__PALADIN_INIT_COLLECT_EXPRESSION__'
