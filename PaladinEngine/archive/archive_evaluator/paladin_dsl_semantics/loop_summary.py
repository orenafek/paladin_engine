from math import floor
from typing import Iterable, Optional, Dict, List, Tuple, Collection

from archive.archive import Rk, Rv
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, LineNo, \
    EvalResultEntry, EvalResultPair
from archive.archive_evaluator.paladin_dsl_semantics.const import Const
from archive.archive_evaluator.paladin_dsl_semantics.const_time import ConstTime
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator, Operator, UniLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.range import Range
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time
from archive.archive_evaluator.paladin_dsl_semantics.time_operator import TimeOperator
from archive.archive_evaluator.paladin_dsl_semantics.union import Union
from archive.archive_evaluator.paladin_dsl_semantics.var_selector import VarSelectorByTimeAndLines, VarSelector
from archive.archive_evaluator.paladin_dsl_semantics.where import Where
from archive.object_builder.object_builder import ObjectBuilder
from stubs.stubs import __SOLI__, __SOL__, __EOLI__


class LoopIteration(BiLateralOperator):
    """
    LoopIteration(<ln>, <i>): Shows changes that have taken place in a loop in row <ln> in its <i>'th index.
                             ** i, v ** must be numbers.
    """

    def __init__(self, times: Iterable[Time], line_no: int, index: int, short: bool = False):
        BiLateralOperator.__init__(self, times, Const(line_no, times), Const(index, times))
        self.is_short = short

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        line_no: int = self.first.eval(builder)[self.times[0]].values[0]
        index: int = self.second.eval(builder)[self.times[0]].values[0]

        loop_iteration_starts_and_ends: List[Tuple[Rk, Rv]] = sorted(builder.get_loop_iterations(line_no),
                                                                     key=lambda t: t[1].time)
        if index * 2 > len(loop_iteration_starts_and_ends) or index * 2 + 1 > len(loop_iteration_starts_and_ends):
            return EvalResult.empty(self.times)

        loop_iteration_start = loop_iteration_starts_and_ends[index * 2]
        loop_iteration_end = loop_iteration_starts_and_ends[index * 2 + 1]
        iterator_values_times = Range(self.times,
                                      ConstTime(self.times, loop_iteration_start[1].time),
                                      ConstTime(self.times, loop_iteration_end[1].time))

        return Union(self.times,
                     *self._create_iteration_operators(iterator_values_times, builder, query_locals,
                                                       range(loop_iteration_start[1].line_no,
                                                             loop_iteration_end[1].line_no + 1))) \
            .eval(builder, query_locals)

    def _create_iteration_operators(self, time_range_operator: Range, builder: ObjectBuilder,
                                    query_locals: Optional[Dict[str, EvalResult]],
                                    line_no_range: range) -> Iterable[Operator]:
        vars_selector_result = \
            VarSelectorByTimeAndLines(self.times, time_range_operator, line_no_range).eval(builder, query_locals)

        if len(vars_selector_result) == 0:
            return EvalResult.empty(self.times)

        changed_vars: Dict[Tuple[str, LineNo], Iterable[Time]] = list(vars_selector_result)[0][
            VarSelector.VARS_KEY].value

        changed_vars_diffs = []
        for v in sorted(changed_vars.keys(), key=lambda _v: _v[0]):
            times = [max(changed_vars[v])] if self.is_short else self.times
            condition_time_op = ConstTime(self.times, times[0]) if self.is_short else time_range_operator
            changed_vars_diffs.append(Where(self.times, Raw(v[0], line_no=v[1], times=times), condition_time_op))

        return changed_vars_diffs


class LoopSummary(UniLateralOperator):
    """
        LoopSummary(<line>): Creates a summary of a loop which header (for i in ...) is in <line>
                             ** <line> should be a Raw Operator, i.e. [[<line>]]
    """

    ITERATION_KEY = 'Iteration'

    def __init__(self, times: Iterable[Time], line_no: int, short: bool = False):
        UniLateralOperator.__init__(self, times, Const(line_no, times))
        self.is_short = short

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        line_no: int = self.first.eval(builder)[self.times[0]].values[0]

        iterations = builder.get_loop_iterations(line_no)
        iterations_count = floor(len(iterations) / 2)

        return Union(self.times,
                     *[LoopIteration(self.times, line_no, i, self.is_short)
                       for i in range(iterations_count)]).eval(builder,
                                                               query_locals) \
            + LoopSummary.__create_iteration_number_result(iterations, builder.get_loop_starts(line_no))

    @staticmethod
    def __create_iteration_number_result(iterations: List[Tuple[Rk, Rv]], loop_starts: List[Tuple[Rk, Rv]]):
        results = []
        i = -1
        for rk, vv in sorted(iterations + loop_starts, key=lambda t: t[1].time):
            if rk.stub_name == __SOL__.__name__:
                i = -1

            if rk.stub_name != __SOLI__.__name__:
                continue

            i += 1
            results.append(EvalResultEntry(vv.time, [EvalResultPair(LoopSummary.ITERATION_KEY, i)], []))

        return EvalResult(results)


class LoopIterationsTimes(UniLateralOperator, TimeOperator):
    """
        LoopIterationsTimes(<ln>): Shows the time ranges in which the iterations of the loop in line <ln> have taken place.
    """

    def __init__(self, times: Iterable[Time], line_no: int):
        UniLateralOperator.__init__(self, times, Const(line_no, times))
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        line_no: int = self.first.eval(builder, query_locals)[0].values[0]

        loop_iteration_starts_and_ends: Collection[Time] = list(
            map(lambda t: t[1].time, sorted(builder.get_loop_iterations(line_no),
                                            key=lambda t: t[1].time)))

        if len(loop_iteration_starts_and_ends) % 2 != 0:
            return EvalResult.empty(self.times)

        loop_iteration_ranges = list(zip(loop_iteration_starts_and_ends[::2], loop_iteration_starts_and_ends[1::2]))

        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t,
                                                       any([start <= t <= end for start, end in loop_iteration_ranges]),
                                                       [])
            for t in self.times])
