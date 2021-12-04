from typing import Any, Union

__PRIMITIVES = [int, float, str, bool, complex]


def ISP(t: type) -> bool:
    return t in __PRIMITIVES


def POID(v: Any) -> Union[Union[int, float, str, bool, complex], int]:
    return v if ISP(type(v)) else id(v)
