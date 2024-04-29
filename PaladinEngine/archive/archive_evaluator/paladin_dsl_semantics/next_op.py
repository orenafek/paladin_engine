from typing import Optional, Dict, Iterable, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time
from archive.archive_evaluator.paladin_dsl_semantics import TimeOperator, Operator
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Next(UniLateralOperator, TimeOperator):
    """
        Next(o): Satisfies for the second time that o has been satisfied ("first after first").
    """

    def __init__(self, times: Iterable[Time], first: Operator):
        UniLateralOperator.__init__(self, times, first)
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        results: EvalResult = self.first.eval(builder)

        satisfaction_iterator = results.satisfies_iterator()
        next(satisfaction_iterator)
        try:
            next_satisfaction_times = list(map(lambda e: e.time, satisfaction_iterator))
        except StopIteration:
            return EvalResult.empty(self.times)

        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t, t in next_satisfaction_times, []) for t in self.times
        ])
