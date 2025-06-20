from typing import Iterable, Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator, Operator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time
from archive.archive_evaluator.paladin_dsl_semantics.time_operator import TimeOperator
from archive.archive_evaluator.paladin_dsl_semantics import Whenever, Not
from archive.object_builder.object_builder import ObjectBuilder


class Until(BiLateralOperator, TimeOperator):

    def __init__(self, times: Iterable[Time], first: Operator, second: Operator):
        BiLateralOperator.__init__(self, times, first, second)
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        first = Whenever(self.times, self.first).eval(builder, query_locals, user_aux)
        second = self.second.eval(builder, query_locals, user_aux)
        not_second = Not(self.times, self.second).eval(builder, query_locals, user_aux)

        min_max_times = range(first.first_satisfaction().time,
                              min(second.last_satisfaction().time + 1, self.times.stop))

        # Both formulas are of type EvalResult:
        """
        ω ⊨ U(ϕ, ψ) ↔ ∃i >= 0, ω_i ⊨ ψ ∧ ∀ <= 0 k <= i, ω_k ⊨ ϕ  
        """
        return EvalResult(
            [TimeOperator.create_time_eval_result_entry(t,
                                                        False
                                                        if t not in min_max_times
                                                        else first[t].satisfies() and not_second[t].satisfies())
             for t in self.times])
