from typing import *

ExpressionMapper = Mapping[str, Dict[int, object]]


class Replacement(NamedTuple):
    expression: str
    value: object
    time: int


EvalResult = Dict[int, Tuple[bool, Optional[List[Replacement]]]]

EvalFunction = Callable[[int, int, int, int], EvalResult]
