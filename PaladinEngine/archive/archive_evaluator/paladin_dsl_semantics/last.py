from typing import Optional, Dict, Iterable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time
from archive.archive_evaluator.paladin_dsl_semantics import TimeOperator, Operator
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Last(UniLateralOperator, TimeOperator):
    """
        Last(<c>): Selects <c> in its last sat
    """

    def __init__(self, times: Iterable[Time], first: Operator):
        UniLateralOperator.__init__(self, times, first)
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = self.first.eval(builder, query_locals)
        return EvalResult(
            [TimeOperator.create_time_eval_result_entry(t, t == first.last_satisfaction().time, []) for t in
             self.times])
