from typing import Iterable, Optional, Dict, Collection, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.const import Const
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time
from archive.archive_evaluator.paladin_dsl_semantics.time_operator import TimeOperator
from archive.object_builder.object_builder import ObjectBuilder


class LineHit(UniLateralOperator, TimeOperator):
    """
    LineHit(ln): Satisfied for each time in which the program has hit line numbered ln.
                 This operator is useful to focus the queries on events that have happened only in a specific line.
    """
    def __init__(self, times: Iterable[Time], line_no: int):
        UniLateralOperator.__init__(self, times, Const(line_no, times))
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None, user_aux: Optional[Dict[str, Callable]] = None):
        line_no: int = self.first.eval(builder, query_locals, user_aux)[0].values[0]

        events: Collection[Time] = list(
            map(lambda t: t[1].time, sorted(builder.find_events(line_no), key=lambda t: t[1].time)))

        return EvalResult([TimeOperator.create_time_eval_result_entry(t, t in events, []) for t in self.times])
