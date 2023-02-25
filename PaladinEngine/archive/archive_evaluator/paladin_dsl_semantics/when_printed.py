from typing import Iterable, Optional, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.const import Const
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.archive_evaluator.paladin_dsl_semantics.time_operator import TimeOperator
from archive.object_builder.object_builder import ObjectBuilder


class WhenPrinted(UniLateralOperator, TimeOperator):
    """
    WhenPrinted(<s>): TimeOperator to find the times in which a string <s> was printed.
    """

    def __init__(self, times: Iterable[Time], output: Raw):
        TimeOperator.__init__(self, times)
        UniLateralOperator.__init__(self, times, Const(output.query, times))

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        str_to_search = self.first.eval(builder, query_locals)[self.times[0]].values[0]

        print_event_times = list(map(lambda r: r[1].time, builder.get_print_events(str_to_search)))

        return EvalResult([TimeOperator.create_time_eval_result_entry(t, t in print_event_times) for t in self.times])
