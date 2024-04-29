from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry
from archive.archive_evaluator.paladin_dsl_semantics.aux_op import AuxOp
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Where(BiLateralOperator, AuxOp):
    """
    Where(s, c): Slice the time range of a query by running s operator only on the times in which c has been satisfied.
                 This operator is useful to retrieve data for a certain time stamps.
    """

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        condition: EvalResult = self.second.eval(builder, query_locals, user_aux)

        # Set times for selector with the results given by condition's eval.
        self.first.update_times(condition.satisfaction_ranges(self.times))

        # Create a sparse results-list with the original time range.
        first_results = self.first.eval(builder, query_locals, user_aux)

        return EvalResult(
            [first_results[time] if time in self.first.times else EvalResultEntry.empty_with_keys(time, first_results[
                time].keys)
             for time in self.times
             ]
        )
