from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.globally import Globally
from archive.archive_evaluator.paladin_dsl_semantics import Not
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.until import Until
from archive.object_builder.object_builder import ObjectBuilder


class Before(BiLateralOperator):

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        return Until(self.times, Not(self.times, Globally(self.times, Not(self.times, self.first))), self.second).eval(
            builder)
