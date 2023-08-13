from typing import Iterable, Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.const import Const
from archive.archive_evaluator.paladin_dsl_semantics.operator import TriLateralOperator, Operator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time, SemanticsUtils
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.object_builder.object_builder import ObjectBuilder


class Bounded(TriLateralOperator):
    def __init__(self, times: Iterable[Time], name: Raw, value: Operator, rest: Operator):
        super(Bounded, self).__init__(times, Const(name.query, times), value, rest)

    def eval(self, eval_data) -> EvalResult:
        # Eval name of first.
        name = SemanticsUtils.get_first(self.times, self.first.eval(eval_data))

        # Eval value of second.
        value_result = self.second.eval(eval_data)

        # Eval rest.
        return self.third.eval(eval_data)
