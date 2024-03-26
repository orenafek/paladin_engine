import copy
from typing import Optional, Dict, Iterable, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time
from archive.archive_evaluator.paladin_dsl_semantics import TimeOperator
from archive.archive_evaluator.paladin_dsl_semantics.first import First
from archive.archive_evaluator.paladin_dsl_semantics.union import Union
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator, Operator
from archive.object_builder.object_builder import ObjectBuilder


class AndThen(BiLateralOperator, TimeOperator):
    """
    AndThan(c, o): Satisfies on the first satisfaction of o after each satisfaction of c.
                   This operator is useful to capture key events that have happened after a known event.
    """

    def __init__(self, times: Iterable[Time], time_op: TimeOperator, op: Operator):
        BiLateralOperator.__init__(self, times, time_op, op)
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        # Evaluate event.
        first_satisfaction = self.first.eval(builder, query_locals, user_aux).satisfaction_ranges(self.times)

        # Create ranges.
        last_time = list(self.times)[::-1][0]
        next_satisfaction_ranges = [range(r.start + 1, r.stop) for r in first_satisfaction if
                                    r.start + 1 <= r.stop and r.start + 1 <= last_time]

        return Union(self.times, *[First(self.times, copy.copy(self.second).update_times(r)) for r in
                                   next_satisfaction_ranges]).eval(builder, query_locals, user_aux)
