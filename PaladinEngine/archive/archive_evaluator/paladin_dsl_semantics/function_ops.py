from typing import Iterable, Optional, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult, LineNo
from archive.archive_evaluator.paladin_dsl_semantics import Const, TimeOperator
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class InFunction(UniLateralOperator, TimeOperator):
    """
    InFunction(f/f@ln): Satisfied for each time in which the program has run the code of f.
    """
    def __init__(self, times: Iterable[Time], func_name: str, line_no: Optional[LineNo] = -1):
        UniLateralOperator.__init__(self, times, Const(func_name, times))
        TimeOperator.__init__(self, times)
        self.func_name = func_name
        self.line_no = line_no

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None) -> EvalResult:
        func_entries_times = list(map(lambda r: r[1].time, builder.get_function_entries(self.func_name, self.line_no)))

        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t, t in func_entries_times, []) for t in self.times
        ])
