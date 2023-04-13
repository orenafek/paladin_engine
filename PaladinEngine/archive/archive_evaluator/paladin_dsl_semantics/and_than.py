from typing import Optional, Dict, Iterable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time
from archive.archive_evaluator.paladin_dsl_semantics import TimeOperator
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class AndThan(TimeOperator, UniLateralOperator):
    """
        AndThan(<event>): Evaluate <event> and return the times right after.
    """

    def __init__(self, time_op: TimeOperator, times: Iterable[Time]):
        TimeOperator.__init__(self, times)
        UniLateralOperator.__init__(self, times, time_op)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        # Evaluate event.
        event_result = self.first.eval(builder, query_locals)

        return EvalResult([
            TimeOperator.create_time_eval_result_entry(e.t, e_next[TimeOperator.TIME_KEY], e.replacements)
            for e, e_next in zip(event_result, event_result[1::])
        ])
