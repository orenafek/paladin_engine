from typing import Optional, Dict, Iterable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time
from archive.archive_evaluator.paladin_dsl_semantics import TimeOperator, Operator
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class After(UniLateralOperator, TimeOperator):
    """
        After(<time_op>): Returns true for all times on the first time <time_op> has been satisfied and later.
    """
    def __init__(self, times: Iterable[Time], first: TimeOperator):
        UniLateralOperator.__init__(self, times, first)
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        first_satisfy: Time = self.first.eval(builder, query_locals).first_satisfaction().time

        if first_satisfy < 0:
            return EvalResult.empty(self.times)

        return EvalResult([TimeOperator.create_time_eval_result_entry(t, t >= first_satisfy) for t in self.times])
