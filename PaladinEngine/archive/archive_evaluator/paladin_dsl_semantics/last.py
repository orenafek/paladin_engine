from typing import Optional, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Last(UniLateralOperator):
    """
        Last(<c>): Selects <c> in the last time it has a value.
    """

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        first = self.first.eval(builder)
        return EvalResult([first.last_satisfaction()])
