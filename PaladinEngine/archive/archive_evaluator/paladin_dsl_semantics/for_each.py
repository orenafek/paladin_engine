from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry, \
    EvalResultPair
from archive.archive_evaluator.paladin_dsl_semantics.operator import TriLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.object_builder.object_builder import ObjectBuilder


class ForEach(TriLateralOperator):
    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        if not isinstance(self.second, Raw):
            return EvalResult.empty(self.times)

        var: str = self.second.query

        iter_res: EvalResult = self.third.eval(builder, query_locals, user_aux)
        if iter_res.is_empty():
            return EvalResult.empty(self.times)

        return EvalResult(self.first.eval(builder, self.query_locals_for_compr(query_locals, var, iter_res), user_aux))

    def query_locals_for_compr(self, query_locals, var: str, iter_res: EvalResult) -> Dict[str, EvalResult]:
        return {**query_locals,
            var: EvalResult(
                [EvalResultEntry(t, [EvalResultPair(k, v) for k, v in iter_res[t].items]) for t in self.times])}
