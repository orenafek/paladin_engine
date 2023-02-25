from typing import Optional, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class First(UniLateralOperator):
    """
        First(<c>): Selects <c> in the first time it exists.
    """

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = self.first.eval(builder)

        first_result = first.first_satisfaction()
        if not first_result:
            return EvalResult.EMPTY()

        return EvalResult([first_result])
