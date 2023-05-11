import typing
from typing import Iterable, Optional, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.changed import Changed
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.archive_evaluator.paladin_dsl_semantics.time_operator import TimeOperator
from archive.object_builder.object_builder import ObjectBuilder


class ChangedInto(BiLateralOperator, TimeOperator):
    def __init__(self, times: Iterable[Time], target: Raw, value: typing.Union[Raw, typing.Any]):
        value = value.query if isinstance(value, Raw) else value
        BiLateralOperator.__init__(self, times, Raw(f'{target.query} == {value}', target.line_no, times),
                                   Changed(times, target))
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        target_with_value = self.first.eval(builder, query_locals).satisfaction_times()
        changed = self.second.eval(builder, query_locals).satisfaction_times()

        return EvalResult(
            [TimeOperator.create_time_eval_result_entry(t, t in target_with_value and t in changed) for t in
             self.times])
