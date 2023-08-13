from typing import Optional, Dict, Iterable, Callable, Any

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time, EvalResultEntry, \
    EvalResultPair
from archive.archive_evaluator.paladin_dsl_semantics.const import Const
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator, Operator
from archive.object_builder.object_builder import ObjectBuilder


class _PureEvalOnce(UniLateralOperator):
    RESULT_KEY = 'RESULT'

    def __init__(self, times: Iterable[Time], first: Operator):
        super().__init__(times, Const(None))
        self.query = first.query

    def eval(self, eval_data) -> EvalResult:
        # queries_cons = {k: v[0].values[0] if len(v) > 0 and len(v[0]) > 0 else None for k, v in query_locals.items()}
        return EvalResult(
            [EvalResultEntry(0, [EvalResultPair(_PureEvalOnce.RESULT_KEY, eval(self.query))])])
            # [EvalResultEntry(0, [EvalResultPair(_PureEvalOnce.RESULT_KEY, eval(self.query, queries_cons))])])

    @staticmethod
    def extract(res: EvalResult):
        return res.first_satisfaction()[_PureEvalOnce.RESULT_KEY].value
