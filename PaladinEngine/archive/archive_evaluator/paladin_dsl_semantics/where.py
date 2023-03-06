from typing import Optional, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Where(BiLateralOperator):
    """
        Where(<selector>, <condition>): Selects <selector> in all times the <condition> is met.
    """

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        condition: EvalResult = self.second.eval(builder)

        # Set times for selector with the results given by condition's eval.
        self.first.update_times(condition.satisfaction_ranges())

        # Create a sparse results-list with the original time range.
        first_results = self.first.eval(builder)

        return EvalResult(
            [first_results[time] if time in self.first.times else EvalResultEntry.empty(time)
             for time in self.times
             ]
        )