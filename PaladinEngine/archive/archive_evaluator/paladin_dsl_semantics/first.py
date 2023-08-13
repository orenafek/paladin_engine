from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class First(UniLateralOperator):
    """
    First(o): Satisfies only for the first time of o.
    """

    def eval(self, eval_data):
        first = self.first.eval(eval_data)

        first_result = first.first_satisfaction()
        if not first_result:
            return EvalResult.empty(self.times)

        return EvalResult(
            [first_result if t == first_result.time else EvalResultEntry.empty_with_keys(t, first_result.keys) for t in
             self.times])
