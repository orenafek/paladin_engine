import os
import time
from concurrent.futures import ThreadPoolExecutor
from math import floor
from typing import Iterable, Optional, Dict, List, Tuple, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, LineNo, \
    EvalResultEntry, EvalResultPair, Rk, Rv
from archive.archive_evaluator.paladin_dsl_semantics.const import Const
from archive.archive_evaluator.paladin_dsl_semantics.in_time import InTime
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator, UniLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.range import Range
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time
from archive.archive_evaluator.paladin_dsl_semantics.summary_op import SummaryOp
from archive.archive_evaluator.paladin_dsl_semantics.time_operator import TimeOperator
from archive.archive_evaluator.paladin_dsl_semantics.union import Union
from archive.archive_evaluator.paladin_dsl_semantics.var_selector import VarSelectorByTimeAndLines, VarSelector
from archive.object_builder.object_builder import ObjectBuilder
from stubs.stubs import __SOLI__, __SOL__


class LoopIteration(BiLateralOperator, SummaryOp):
    """
    LoopIteration(ln, i): Retrieve any events that have happened in the loop's code's line numbers in the i'th iteration
                          of the loop that starts in line ln.
    """

    def __init__(self, times: Iterable[Time], line_no: int, index: int, short: bool = False, parallel: bool = True):
        BiLateralOperator.__init__(self, times, Const(line_no, times, parallel), Const(index, times, parallel),
                                   parallel)
        self.is_short = short
        self.line_no = line_no
        self.index = index

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        line_no: int = self.line_no
        index: int = self.index

        iteration = self.create_iteration(self.times, line_no, index, builder, query_locals, user_aux)
        ops = []
        for (expr, line_no), rngs in iteration.items():
            times = [i for r in rngs for i in r]
            ops.append(Raw(expr, line_no, times=times, parallel=True))

        return Union(self.times, *ops, parallel=self.parallel).eval(builder, query_locals, user_aux)

    @classmethod
    def _create_iteration_operators(cls, times: Iterable[time], time_range_operator: Range, builder: ObjectBuilder,
                                    query_locals: Optional[Dict[str, EvalResult]],
                                    user_aux: Optional[Dict[str, Callable]],
                                    line_no_range: range) -> Dict:
        vars_selector_result = \
            VarSelectorByTimeAndLines(times, time_range_operator, line_no_range).eval(builder, query_locals, user_aux)

        if len(vars_selector_result) == 0:
            return {}

        changed_vars: Dict[Tuple[str, LineNo], Iterable[Time]] = list(vars_selector_result)[0][
            VarSelector.VARS_KEY].value

        d = {}
        for v in sorted(changed_vars.keys(), key=lambda _v: _v[0]):
            if v not in d:
                d[v] = []
            d[v].append(range(time_range_operator.first.const_time, time_range_operator.second.const_time))

        return d

    @classmethod
    def create_iteration(cls, times: Iterable[Time], line_no: LineNo, index: int, builder: ObjectBuilder,
                         query_locals: Optional[Dict[str, EvalResult]], user_aux: Optional[Dict[str, Callable]]):
        loop_iteration_starts_and_ends: List[Tuple[Rk, Rv]] = sorted(builder.get_loop_iterations(line_no),
                                                                     key=lambda t: t[1].time)
        if index * 2 > len(loop_iteration_starts_and_ends) or index * 2 + 1 > len(loop_iteration_starts_and_ends):
            return {}

        loop_iteration_start = loop_iteration_starts_and_ends[index * 2]
        loop_iteration_end = loop_iteration_starts_and_ends[index * 2 + 1]

        iterator_values_times = Range(times,
                                      InTime(times, loop_iteration_start[1].time + 1),
                                      InTime(times, loop_iteration_end[1].time - 1))

        return cls._create_iteration_operators(times, iterator_values_times, builder, query_locals, user_aux,
                                               range(loop_iteration_start[1].line_no,
                                                     loop_iteration_end[1].line_no + 1))


class LoopSummary(UniLateralOperator, SummaryOp):
    """
    LoopSummary(ln): Retrieve any events that have happened in the loop's code's line numbers of the loop that starts in
                     line ln, i.e., runs LoopIteration for each iteration of the loop.
    """

    ITERATION_KEY = 'Iteration'

    def __init__(self, times: Iterable[Time], line_no: int, short: bool = False, parallel: bool = False):
        UniLateralOperator.__init__(self, times, Const(line_no, times, parallel=parallel), parallel=parallel)
        self.is_short = short

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        line_no: int = self.first.eval(builder)[self.times[0]].values[0]

        iterations = builder.get_loop_iterations(line_no)
        iterations_count = floor(len(iterations) / 2)

        with ThreadPoolExecutor(os.cpu_count()) as executor:
            loop_iterations = list(executor.map(
                lambda i: LoopIteration.create_iteration(self.times, line_no, i, builder, query_locals, user_aux),
                range(iterations_count)
            ))

        dd = {}
        for d in loop_iterations:
            for k, v in d.items():
                if k not in dd:
                    dd[k] = []
                dd[k].append(v)

        ops = []
        for (expr, line_no), rngs in dd.items():
            times = [i for r in rngs for i in r]
            ops.append(Raw(expr, line_no, times=times, parallel=True))

        union_result = Union(self.times, *ops, parallel=True).eval(builder, query_locals, user_aux)
        iteration_number_result = self.__create_iteration_number_result(iterations, builder.get_loop_starts(line_no))

        return union_result + iteration_number_result

    @staticmethod
    def __create_iteration_number_result(iterations: List[Tuple[Rk, Rv]], loop_starts: List[Tuple[Rk, Rv]]):
        results = []

        def process_iteration(rk_vv):
            rk, vv = rk_vv
            nonlocal i
            if rk.stub_name == __SOL__.__name__:
                i = -1
            if rk.stub_name != __SOLI__.__name__:
                return None
            i += 1
            return EvalResultEntry(vv.time, [EvalResultPair(LoopSummary.ITERATION_KEY, i)], [])

        i = -1
        with ThreadPoolExecutor(os.cpu_count()) as executor:
            futures = list(executor.map(process_iteration, sorted(iterations + loop_starts, key=lambda t: t[1].time)))

        results.extend(filter(None, futures))
        return EvalResult(results)


class LoopIterationsTimes(UniLateralOperator, TimeOperator):
    """
        LoopIterationsTimes(<ln>): Shows the time ranges in which the iterations of the loop in line <ln> have taken place.
    """

    def __init__(self, times: Iterable[Time], line_no: int):
        UniLateralOperator.__init__(self, times, Const(line_no, times))
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        line_no: int = self.first.eval(builder, query_locals, user_aux)[0].values[0]

        # Retrieve loop iterations in parallel
        with ThreadPoolExecutor(os.cpu_count()) as executor:
            loop_iterations = list(executor.map(
                lambda t: t[1].time,
                sorted(builder.get_loop_iterations(line_no), key=lambda t: t[1].time)
            ))

        if len(loop_iterations) % 2 != 0:
            return EvalResult.empty(self.times)

        loop_iteration_ranges = list(zip(loop_iterations[::2], loop_iterations[1::2]))

        # Process time evaluation in parallel
        def create_time_eval_result_entry(t):
            return TimeOperator.create_time_eval_result_entry(
                t,
                any(start <= t <= end for start, end in loop_iteration_ranges),
                []
            )

        with ThreadPoolExecutor(os.cpu_count()) as executor:
            eval_results = list(executor.map(create_time_eval_result_entry, self.times))

        return EvalResult(eval_results)
