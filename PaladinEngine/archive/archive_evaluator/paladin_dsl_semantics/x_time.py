from typing import Iterable, Optional, Dict, cast

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult
from archive.archive_evaluator.paladin_dsl_semantics import Operator, TimeOperator, Const, Next
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class XTime(BiLateralOperator, TimeOperator):

    def __init__(self, times: Iterable[Time], event: Operator, number: int):
        BiLateralOperator.__init__(self, times, event, Const(number, times))
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        number = cast(Const, self.second).eval_const_value(builder, query_locals)

        if number < 0:
            return EvalResult.empty(self.times)

        event: Operator = self.first
        for n in range(number):
            event = Next(self.times, event)

        return event.eval(builder, query_locals)

