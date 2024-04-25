from typing import Iterable, Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator, Operator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time
from archive.archive_evaluator.paladin_dsl_semantics.time_operator import TimeOperator
from archive.object_builder.object_builder import ObjectBuilder


class Range(BiLateralOperator, TimeOperator):
    """
        Range(o1, o2): Satisfies on each time in between the first satisfaction of o1 and the last satisfaction of o2.
    """

    def __init__(self, times: Iterable[Time], first: Operator, second: Operator):
        BiLateralOperator.__init__(self, times, first, second)
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        first = self.first.eval(builder, query_locals, user_aux)
        second = self.second.eval(builder, query_locals, user_aux)

        first_satisfaction = first.first_satisfaction().time
        last_satisfaction = second.last_satisfaction().time

        if first_satisfaction < 0 or last_satisfaction < 0:
            return EvalResult.empty(self.times)

        min_max_times = range(first_satisfaction, min(last_satisfaction + 1, self.times.stop))

        return EvalResult([TimeOperator.create_time_eval_result_entry(t, t in min_max_times) for t in self.times])
