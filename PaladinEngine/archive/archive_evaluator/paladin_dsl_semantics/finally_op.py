from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import TRUE
from archive.archive_evaluator.paladin_dsl_semantics.until import Until
from archive.object_builder.object_builder import ObjectBuilder


class Finally(UniLateralOperator):
    def eval(self, eval_data):
        return Until(self.times, TRUE, self.first).eval(eval_data)
