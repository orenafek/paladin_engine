from typing import Iterable, Optional, Dict, Callable, Tuple, Any, cast

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult, EvalResultEntry, \
    EvalResultPair
from archive.archive_evaluator.paladin_dsl_semantics import InTime
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder
from stubs.stubs import __AS__, __FC__


class What(UniLateralOperator):
    def __init__(self, times: Iterable[Time], time: Time | Iterable[Time]):
        super().__init__(times, InTime(times, time))
        self.time_range = time if isinstance(time, Iterable) else [time]

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        if any(t not in self.times for t in self.time_range):
            return EvalResult.empty(self.times)

        events = builder.find_events(time_range=self.time_range)

        return EvalResult([
            EvalResultEntry(t, [
                EvalResultPair(*What._event_to_pair(t, builder, *e)) for e in events])
            if t in self.time_range else EvalResultEntry.empty(t)
            for t in self.times
        ])

    @staticmethod
    def _event_to_pair(t: Time, builder: ObjectBuilder, rk: Archive.Record.RecordKey, vv: Archive.Record.RecordValue) -> \
            Tuple[str, Any]:
        key = f'{vv.expression}@{vv.line_no}'
        match rk.stub_name:
            case __AS__.__name__:
                return key, builder.build(cast(str, vv.value), t, vv.line_no)
            case __FC__.__name__:
                return key + '()', builder.build(cast(str, vv.value), t, vv.line_no)
            case _:
                return '', ''
