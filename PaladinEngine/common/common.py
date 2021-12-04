from typing import Any, Union

__PRIMITIVES = [int, float, str, bool, complex]


def ISP(t: type) -> bool:
    return t in __PRIMITIVES


def POID(v: Any) -> Union[Union[int, float, str, bool, complex], int]:
    return v if ISP(type(v)) else id(v)


PALADIN_OBJECT_COLLECTION_FIELD = '__PALADIN_INIT_COLLECT__'
PALADIN_OBJECT_COLLECTION_EXPRESSION = '__PALADIN_INIT_COLLECT_EXPRESSION__'