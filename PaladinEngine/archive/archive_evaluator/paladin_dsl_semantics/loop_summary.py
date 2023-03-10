from math import floor
from typing import Iterable, Optional, Dict, List, Tuple, Collection

from archive.archive import Rk, Rv, Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.const import Const
from archive.archive_evaluator.paladin_dsl_semantics.const_time import ConstTime
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator, Operator, UniLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time
from archive.archive_evaluator.paladin_dsl_semantics.range import Range
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.archive_evaluator.paladin_dsl_semantics.time_operator import TimeOperator
from archive.archive_evaluator.paladin_dsl_semantics.var_selector import VarSelectorByTimeAndLines, VarSelector
from archive.archive_evaluator.paladin_dsl_semantics.where import Where
from archive.archive_evaluator.paladin_dsl_semantics.union import Union
from archive.object_builder.object_builder import ObjectBuilder


class LoopIteration(BiLateralOperator):
    """
    LoopIteration(<ln>, <i>): Shows changes that have taken place in a loop in row <ln> in its <i>'th index.
                             ** i, v ** must be numbers.
    """

    def __init__(self, times: Iterable[Time], line_no: int, index: int):
        BiLateralOperator.__init__(self, times, Const(line_no, times), Const(index, times))

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

        return Union(self.times, *self._create_iterations_operators(iterator_values_times, builder, query_locals,
                                                                    range(loop_iteration_start[1].line_no,
                                                                          loop_iteration_end[1].line_no + 1))) \
            .eval(builder, query_locals)

    def _create_iterations_operators(self, time_range_operator: Range, builder: Archive,
                                     query_locals: Optional[Dict[str, EvalResult]],
                                     line_no_range: range) -> Iterable[Operator]:
        vars_selector_result = VarSelectorByTimeAndLines(self.times, time_range_operator, line_no_range).eval(builder,
                                                                                                              query_locals)

        if len(vars_selector_result) == 0:
            return EvalResult.empty(self.times)

        changed_vars = list(vars_selector_result)[0][VarSelector.VARS_KEY].value
        changed_vars_diffs = []
        for v in sorted(changed_vars):
            ###
            # FIXME: The var is not located using a specific scope in here (line_no=-1)
            #  therefore other vars can get in the way...
            #  For example:
            #  ```
            #   1: for i in range(1,4):
            #      j = 1
            #      ...
            #   10: for i in range(5,8):
            #     ...
            #  ```
            #  If We look for the first iter of the second loop (i == 5), with LoopIteration([[i]]@10, [[5]]),
            #  the last value of the first iteration (i@1 == 4) will also be presented.
            #  There is Currently a trouble to fix this, because i have a scope (i@10) but after the VarSelection,
            #  j@10 is incorrect.
            #
            #  TODO: Maybe if a range of lines that compound the loop is used, a range of scopes can be used:
            #   E.g.: LoopIteration([[i]], [[0]], 1, 10)
            ###
            selector = Raw(v, times=self.times)
            changed_vars_diffs.append(Where(self.times, selector, time_range_operator))

        return changed_vars_diffs


class LoopSummary(UniLateralOperator):
    """
        LoopSummary(<line>): Creates a summary of a loop which header (for i in ...) is in <line>
                             ** <line> should be a Raw Operator, i.e. [[<line>]]
    """

    def __init__(self, times: Iterable[Time], line_no: int):
        UniLateralOperator.__init__(self, times, Const(line_no, times))

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        line_no: int = self.first.eval(builder)[self.times[0]].values[0]

        iterations = floor(len(builder.get_loop_iterations(line_no)) / 2)

        return Union(self.times, *[LoopIteration(self.times, line_no, i) for i in range(iterations)]).eval(builder,
                                                                                                           query_locals)


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
