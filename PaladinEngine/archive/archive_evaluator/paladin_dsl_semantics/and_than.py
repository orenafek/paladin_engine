import copy
from typing import Optional, Dict, Iterable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time
from archive.archive_evaluator.paladin_dsl_semantics import TimeOperator
from archive.archive_evaluator.paladin_dsl_semantics.first import First
from archive.archive_evaluator.paladin_dsl_semantics.union import Union
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator, Operator
from archive.object_builder.object_builder import ObjectBuilder


class AndThan(BiLateralOperator, TimeOperator):
    """
        AndThan(<time_op>, <op>): Return the first satisfactory of <op> after each satisfaction of <time_op>
    """

    def __init__(self, times: Iterable[Time], time_op: TimeOperator, op: Operator):
        BiLateralOperator.__init__(self, times, time_op, op)
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        # Evaluate event.
        first_satisfaction = list(self.first.eval(builder, query_locals).satisfies_iterator())
        satisfaction_pairs = list(zip([e.time for e in first_satisfaction], [e.time for e in first_satisfaction][1::]))

        # Create ranges.
        last_time = list(self.times)[::-1][0]
        next_satisfaction_ranges = [range(p[0] + 1, p[1]) for p in satisfaction_pairs if p[0] + 1 < last_time]

        return Union(self.times, *[First(self.times, copy.copy(self.second).update_times(r)) for r in
                                   next_satisfaction_ranges]).eval(builder, query_locals)
