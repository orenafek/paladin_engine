from typing import Optional, Dict, Iterable, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time, EvalResultEntry, \
    EvalResultPair, EVAL_BUILTIN_CLOSURE
from archive.archive_evaluator.paladin_dsl_semantics.const import Const
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator, Operator
from archive.object_builder.object_builder import ObjectBuilder


class _PureEvalOnce(UniLateralOperator):
    RESULT_KEY = 'RESULT'

    def __init__(self, times: Iterable[Time], first: Operator):
        super().__init__(times, Const(None))
        self.query = first.query

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        return EvalResult(
            [EvalResultEntry(0, [EvalResultPair(_PureEvalOnce.RESULT_KEY, eval(self.query, EVAL_BUILTIN_CLOSURE))])])
