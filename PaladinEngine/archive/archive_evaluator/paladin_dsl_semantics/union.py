import concurrent.futures
import os
from functools import reduce
from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.aux_op import AuxOp
from archive.archive_evaluator.paladin_dsl_semantics.operator import VariadicLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Union(VariadicLateralOperator, AuxOp):
    """
    Union(o1, ..., on): Joins any number of operators together.
                        The operator returns the union of all time stamps and outer join of all os' columns.
    """

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            # Submit evaluation tasks for each argument in self.args
            futures = [executor.submit(arg.eval, builder, query_locals, user_aux) for arg in self.args]

            # Collect the results of the evaluation
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Join the results using EvalResult.join
        return reduce(lambda r1, r2: EvalResult.join(r1, r2), results, EvalResult.empty(self.times))
