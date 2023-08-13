from typing import Iterable, Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult
from archive.archive_evaluator.paladin_dsl_semantics import BiTimeOperator, Operator, TimeOperator, Whenever
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class And(BiTimeOperator):
    def __init__(self, times: Iterable[Time], first: Operator, second: Operator):
        super().__init__(times, first, second, lambda r1, r2: r1 and r2)


class Or(BiTimeOperator):
    def __init__(self, times: Iterable[Time], first: Operator, second: Operator):
        super().__init__(times, first, second, lambda r1, r2: r1 or r2)


class Not(UniLateralOperator, TimeOperator):

    def __init__(self, times: Iterable[Time], first: Operator):
        UniLateralOperator.__init__(self, times, first)
        TimeOperator.__init__(self, times)

    def eval(self, eval_data):
        first = Whenever(self.times, self.first).eval(eval_data)

        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t, not first[t].satisfies(), first[t].replacements)
            for t in self.times])
