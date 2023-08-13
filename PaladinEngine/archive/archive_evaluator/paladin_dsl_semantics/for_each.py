from typing import Optional, Dict, Iterable, cast, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time, EvalResultEntry, \
    EvalResultPair
from archive.archive_evaluator.paladin_dsl_semantics.operator import Operator, BiLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.const import Const
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.object_builder.object_builder import ObjectBuilder


class ForEach(BiLateralOperator):

    def __init__(self, times: Iterable[Time], first: str | Raw, second: Operator):
        super().__init__(times, Const(first if isinstance(first, str) else first.query), second)

    def eval(self, eval_data) -> EvalResult:
        second_res = self.second.eval(eval_data)
        second_res_keys = second_res.all_keys()
        return Raw(cast(Const, self.first).const, times=self.times) \
            .eval(eval_data)
