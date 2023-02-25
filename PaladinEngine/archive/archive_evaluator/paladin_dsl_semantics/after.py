from typing import Optional, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.before import Before
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class After(BiLateralOperator):

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        return Before(self.times, self.second, self.first).eval(builder)
