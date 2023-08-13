from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.globally import Globally
from archive.archive_evaluator.paladin_dsl_semantics.next_op import Next
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class AllFuture(UniLateralOperator):
    def eval(self, eval_data):
        return Globally(self.times, Next(self.times, self.first))
