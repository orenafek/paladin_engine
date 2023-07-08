from typing import Optional, Dict, Iterable, cast, Any, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time, EvalResultEntry, \
    EvalResultPair
from archive.archive_evaluator.paladin_dsl_semantics.pure_eval_once import _PureEvalOnce
from archive.archive_evaluator.paladin_dsl_semantics.operator import Operator, BiLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Let(BiLateralOperator):
    LET_BOUNDED_KEY = 'BOUNDED'

    def __init__(self, times: Iterable[Time], first: str, second: Operator):
        super().__init__(times, _PureEvalOnce(times, first), second)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        bounded_vars: Dict[str, Any] = cast(Dict[str, Any], self.first.eval(builder, query_locals, user_aux).first_satisfaction()[
            _PureEvalOnce.RESULT_KEY].value)
        bounded_vars_results = {v: EvalResult(
            [EvalResultEntry(t, [EvalResultPair(Let.LET_BOUNDED_KEY, bounded_vars[v])]) for t in self.times]) for v in
            bounded_vars}
        return self.second.eval(builder, {**query_locals, **bounded_vars_results}, user_aux)
