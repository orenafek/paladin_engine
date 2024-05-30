from typing import Iterable, Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time
from archive.archive_evaluator.paladin_dsl_semantics.time_operator import TimeOperator
from archive.object_builder.object_builder import ObjectBuilder


class InTime(TimeOperator):
    """
        InTime(t): Satisfies only on time t. Useful if an event time is known.
    """

    def __init__(self, times: Iterable[Time], const_time: int):
        super().__init__(times)
        self.const_time = const_time

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t, t == self.const_time, [])
            for t in self.times
        ])


class InTimeRange(TimeOperator):
    """
        InTimeRange(t1, t2): Satisfies for times in the inclusive range of t1 and t2. I.e.: True ⟺ t ∈ [t1, t2]
    """

    def __init__(self, times: Iterable[Time], left: Time, right: Time):
        super().__init__(times)
        self.const_time_range = range(left, right + 1)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t, t in self.const_time_range, []) for t in self.times
        ])
