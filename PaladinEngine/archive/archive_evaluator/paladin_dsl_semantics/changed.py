from typing import Optional, Dict, Iterable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time, LineNo
from archive.archive_evaluator.paladin_dsl_semantics import TimeOperator, Operator, Const, Raw
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Changed(UniLateralOperator, TimeOperator):
    """
        Changed(<n>): All times in which n has been changed, either assigned to (if it's a variable) or internally
        (for a builtin collection (list, dict, set, tuple) or an object).
    """

    def __init__(self, times: Iterable[Time], first: Raw):
        UniLateralOperator.__init__(self, times, first)
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        if not isinstance(self.first, Raw):
            return EvalResult.empty(self.times)

        change_times: Iterable[Time] = builder.get_change_times(self.first.query, self.first.line_no)
        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t, t in change_times, []) for t in self.times
        ])