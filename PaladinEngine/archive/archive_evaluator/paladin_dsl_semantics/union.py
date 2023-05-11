from functools import reduce
from typing import Optional, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.operator import VariadicLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Union(VariadicLateralOperator):
    """
    Union(o1, ..., on): Joins any number of operators together.
                        The operator returns the union of all time stamps and outer join of all os' columns.
    """

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        return reduce(lambda r1, r2: EvalResult.join(r1, r2),
                      map(lambda arg: arg.eval(builder, query_locals), self.args),
                      EvalResult.empty(self.times))
