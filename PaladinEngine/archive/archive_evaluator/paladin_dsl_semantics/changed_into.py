import typing
from typing import Iterable, Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.changed import Changed
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.archive_evaluator.paladin_dsl_semantics.time_operator import TimeOperator
from archive.object_builder.object_builder import ObjectBuilder


class ChangedInto(BiLateralOperator, TimeOperator):
    """
    ChangedInto(e/e@ln, v): Satisfied for each time in which e has been changed into a value v.
                            This operator is useful to focus the queries on times that events have happened,
                            instead of when an expression had a value, i.e.,
                            the first time it had that value rather on every time since.
    """

    def __init__(self, times: Iterable[Time], target: Raw, value: typing.Union[Raw, typing.Any]):
        value = value.query if isinstance(value, Raw) else value
        BiLateralOperator.__init__(self, times, Raw(f'{target.query} == {value}', target.line_no, times),
                                   Changed(times, target))
        TimeOperator.__init__(self, times)

    def eval(self, eval_data):
        target_with_value = self.first.eval(eval_data).satisfaction_times()
        changed = self.second.eval(eval_data).satisfaction_times()

        return EvalResult(
            [TimeOperator.create_time_eval_result_entry(t, t in target_with_value and t in changed) for t in
             self.times])
