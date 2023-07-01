from typing import Optional, Dict, Iterable, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time
from archive.archive_evaluator.paladin_dsl_semantics import TimeOperator, Operator
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Last(UniLateralOperator, TimeOperator):
    """
        Last(o): Satisfies only for the last time of o.
    """

    def __init__(self, times: Iterable[Time], first: Operator):
        UniLateralOperator.__init__(self, times, first)
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        first = self.first.eval(builder, query_locals, user_aux)
        return EvalResult(
            [TimeOperator.create_time_eval_result_entry(t, t == first.last_satisfaction().time, []) for t in
             self.times])
