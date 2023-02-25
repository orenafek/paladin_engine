from typing import Optional, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Next(UniLateralOperator):
    """
        Next(<c>): Returns the second satisfaction of <c> (next after first)
    """

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        formula_result = self.first.eval(builder)
        if formula_result is bool:
            """
            Next(T) = T
            Next(F) = F
            """
            return formula_result

        first = formula_result.first_satisfaction()

        return [r if r.time != first.time else r.create_const_copy(False) for r in formula_result]
