from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import FALSE
from archive.archive_evaluator.paladin_dsl_semantics.release import Release
from archive.object_builder.object_builder import ObjectBuilder


class Globally(UniLateralOperator):
    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        return Release(self.times, FALSE(self.times), self.first).eval(builder)
