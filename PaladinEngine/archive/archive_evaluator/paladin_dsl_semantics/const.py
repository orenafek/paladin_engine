from typing import Iterable, Optional, Dict, Collection, Any as AnyT, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry, \
    EvalResultPair, Time
from archive.archive_evaluator.paladin_dsl_semantics.operator import Operator
from archive.object_builder.object_builder import ObjectBuilder


class Const(Operator):
    CONST_KEY = 'CONST'

    def __init__(self, const, times: Iterable[Time] = None):
        super(Const, self).__init__(times if times else [range(0, 1)])
        self.const = const

    def eval(self, eval_data):
        return EvalResult([EvalResultEntry(t, [EvalResultPair(Const.CONST_KEY, self.const)], []) for t in self.times])

    def _get_args(self) -> Collection['Operator']:
        return []

    def eval_const_value(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None) -> AnyT:
        return self.eval(eval_data)[self.times[0]].values[0]
