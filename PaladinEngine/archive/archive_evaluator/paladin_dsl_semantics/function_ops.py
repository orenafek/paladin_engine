from typing import Iterable, Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult, LineNo
from archive.archive_evaluator.paladin_dsl_semantics.const import Const
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import TRUE
from archive.archive_evaluator.paladin_dsl_semantics.time_operator import TimeOperator
from archive.archive_evaluator.paladin_dsl_semantics.union import Union
from archive.archive_evaluator.paladin_dsl_semantics.var_selector import VarSelector, _VarSelectorByEntries
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

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        func_entries_times = list(map(lambda r: r[1].time, builder.get_function_entries(self.func_name, self.line_no)))

        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t, t in func_entries_times, []) for t in self.times
        ])


class Locals(UniLateralOperator):
    """
    Locals(f/f@ln): Retrieves values of all assignments that have happened inside a function.
    """

    def __init__(self, times: Iterable[Time], func_name: str, line_no: Optional[LineNo] = -1):
        UniLateralOperator.__init__(self, times, TRUE)
        self.func_name = func_name
        self.line_no = line_no

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        func_entries = builder.get_function_entries(self.func_name, self.line_no,
                                                    entrances=False,
                                                    exits=False,
                                                    ass_and_bmfcs_only=True)
        var_selector = _VarSelectorByEntries(self.times, func_entries)
        vars = getattr(var_selector.eval(builder, query_locals)[0], VarSelector.VARS_KEY)


        selectors = [Raw(var_name, line_no, self.times) for (var_name, line_no), times in vars.items()
                     if self._valid_var(var_name)]

        return Union(self.times, *selectors).eval(builder, query_locals, user_aux)

    def _valid_var(self, var_name: str) -> bool:
        return not var_name.startswith('[')
