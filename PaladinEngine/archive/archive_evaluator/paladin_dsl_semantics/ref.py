from abc import abstractmethod
from typing import Iterable, Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult
from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import QUERY_RES
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Ref(UniLateralOperator):
    def __init__(self, times: Iterable[Time]):
        super().__init__(times, None)

    @abstractmethod
    def ref_key(self):
        raise NotImplementedError()

    def eval(self, eval_data) -> EvalResult:
        try:
            return eval_data.query_locals[self.ref_key()]

        except KeyError:
            return EvalResult.empty(self.times)


class QueryRef(Ref):

    def __init__(self, times: Iterable[Time], num: int):
        super().__init__(times)
        self.query_num = num

    def ref_key(self, *args):
        return QUERY_RES(self.query_num)


class OpRef(Ref):
    def __init__(self, times: Iterable[Time], op_var_name: str):
        super().__init__(times)
        self.op_var_name = op_var_name

    def ref_key(self):
        return self.op_var_name

