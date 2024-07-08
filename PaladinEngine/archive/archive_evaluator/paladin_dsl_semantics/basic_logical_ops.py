import os
from typing import Iterable, Optional, Dict, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult
from archive.archive_evaluator.paladin_dsl_semantics import BiTimeOperator, Operator, TimeOperator, Whenever
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class And(BiTimeOperator):
    """
        And(o1, o2): Satisfied for each time that satisfies both o1 and o2.
    """

    def __init__(self, times: Iterable[Time], first: Operator, second: Operator, parallel: bool = False):
        super().__init__(times, first, second, lambda r1, r2: r1 and r2, parallel)


class Or(BiTimeOperator):
    """
        Or(o1, o2): Satisfies for each time that satisfies either o1 or o2.
    """

    def __init__(self, times: Iterable[Time], first: Operator, second: Operator):
        super().__init__(times, first, second, lambda r1, r2: r1 or r2)


class Not(UniLateralOperator, TimeOperator):
    """
        Not(o): Satisfies for each time that doesn't satisfy o.
    """

    def __init__(self, times: Iterable[Time], first: Operator, parallel: bool = False):
        UniLateralOperator.__init__(self, times, first, parallel)
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        if isinstance(self.first, TimeOperator):
            first = self.first.eval(builder, query_locals, user_aux)
            logical_not = lambda e: (not e[TimeOperator.TIME_KEY].value) if TimeOperator.TIME_KEY in e else True
        else:
            first = Whenever(self.times, self.first).eval(builder, query_locals, user_aux)
            logical_not = lambda e: not e.satisfies()

        process_entry = lambda e, log_not: TimeOperator.create_time_eval_result_entry(e.time, log_not(e))

        with ThreadPoolExecutor(os.cpu_count()) as executor:
            futures = [executor.submit(process_entry, e, logical_not) for e in first]
            results = [future.result() for future in as_completed(futures)]

        return EvalResult(results)



