from typing import Iterable, Optional, Dict, List, Tuple

from archive.archive import Rk, Rv
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.const import Const
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.archive_evaluator.paladin_dsl_semantics.var_selector import VarSelector, VarSelectorByLineNo
from archive.object_builder.object_builder import ObjectBuilder


class Line(UniLateralOperator):
    """
        Line(<number>): Returns values of all values in the scope of <number> when the program hit line numbered <number>.
    """

    def __init__(self, times: Iterable[Time], line_no: int):
        UniLateralOperator.__init__(self, times, Const(line_no, times))

    def eval(self, builder: ObjectBuilder,
             query_locals: Optional[Dict[str, EvalResult]] = None) -> EvalResult:
        line_no = self.first.eval(builder)[self.times[0]].values[0]
        events_by_line_no: List[Tuple[Rk, Rv]] = builder.find_events(line_no)
        if not events_by_line_no:
            return EvalResult.empty(self.times)

        event_times = list(map(lambda t: t[1].time, events_by_line_no))
        event_times = event_times if event_times[0] == 0 else [0] + event_times
        ranges = [(t1, t2) for t1, t2 in zip(event_times, event_times[1::])]
        results = EvalResult.empty(self.times)

        for r in ranges:
            time_range = range(r[0], r[1] + 1)
            vars = VarSelectorByLineNo(self.times, Const(True, times=time_range), line_no).eval(builder)
            if not vars or not vars[r[1]].__getitem__(VarSelector.VARS_KEY).value:
                continue

            for v in vars[r[1]].__getitem__(VarSelector.VARS_KEY).value:
                results = results.join(results, Raw(v[0], v[1], time_range).eval(builder))

        return results
