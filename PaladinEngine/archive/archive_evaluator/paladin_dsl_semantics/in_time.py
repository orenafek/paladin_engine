from typing import Iterable, Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult
from archive.archive_evaluator.paladin_dsl_semantics import Operator
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class InTime(BiLateralOperator):
    def __init__(self, times: Iterable[Time], op: Operator, t: Time):
        super().__init__(times, op, None)
        self.specific_time = t

    def eval(self, eval_data) -> EvalResult:

        res = self.first.eval(eval_data)

        return EvalResult.duplicate(res[self.specific_time], self.times)

