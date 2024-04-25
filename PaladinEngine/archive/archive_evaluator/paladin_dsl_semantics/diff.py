from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import TRUE
from archive.archive_evaluator.paladin_dsl_semantics.where import Where
from archive.object_builder.object_builder import ObjectBuilder


class Diff(BiLateralOperator):
    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        time_range = self.second.eval(builder)
        selector_results = {}
        for r in satisfaction_ranges(time_range):
            self.update_times([r])
            tr = range(r.start - 1, r.start)
            before_first_results = Where(times=tr, first=self.first.update_times([tr]), second=TRUE).eval(builder)
            self.update_times([r])
            selector_results.update(before_first_results)
            selector_results.update(Where(self.times, self.first, self.second).eval(builder))

        return selector_results
