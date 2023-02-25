from typing import Iterable, Optional, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time
from archive.archive_evaluator.paladin_dsl_semantics.time_operator import TimeOperator
from archive.object_builder.object_builder import ObjectBuilder


class ConstTime(TimeOperator):

    def __init__(self, times: Iterable[Time], const_time: int):
        super().__init__(times)
        self.const_time = const_time

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t, t == self.const_time, [])
            for t in self.times
        ])
