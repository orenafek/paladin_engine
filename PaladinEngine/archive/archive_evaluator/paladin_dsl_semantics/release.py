from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics import Not
from archive.archive_evaluator.paladin_dsl_semantics.until import Until
from archive.object_builder.object_builder import ObjectBuilder


class Release(BiLateralOperator):

    def eval(self, eval_data):
        return Not(self.times, Until(self.times, Not(self.times, self.first), Not(self.times, self.second))).eval(eval_data)
