from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry, \
    EvalResultPair
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Group(UniLateralOperator):
    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        res = self.first.eval(builder, query_locals, user_aux)

        return EvalResult([
            EvalResultEntry(t, [EvalResultPair('k', {k: v for k, v in res[t].items()})], []) for t in self.times])
