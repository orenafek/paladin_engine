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

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        # Eval name of first.
        name = SemanticsUtils.get_first(self.times, self.first.eval(builder, query_locals, user_aux))

        # Eval value of second.
        value_result = self.second.eval(builder, query_locals, user_aux)

        # Eval rest.
        return self.third.eval(builder, {**query_locals, name: value_result})
