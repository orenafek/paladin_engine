from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import SemanticsUtils
from archive.object_builder.object_builder import ObjectBuilder


class NextAfter(BiLateralOperator):
    def eval(self, eval_data):
        a = self.first.eval(eval_data)
        b = self.second.eval(eval_data)

        if isinstance(a, bool) or isinstance(b, bool):
            raise TypeError('Cannot find NextAfter if either of the queries are bool')

        replacements_times = lambda er: [t for t in er if any(rep.time == t for rep in er[t][1])]

        a_times = replacements_times(a)
        b_times = replacements_times(b)

        time_ranges = zip(a_times, a_times[1::])
        b_relevant_keys = list(
            map(lambda time_range: next((t for t in b_times if t in range(*time_range)), None), time_ranges))

        """{t:r for t, r in b.items() if t in list( map(lambda time_range: next((t for t in [t for t in b if any(
        rep.time == t for rep in b[t][1])] if t in range(*time_range)), None), list(zip([t for t in a if any(rep.time 
        == t for rep in a[t][1])], [t for t in a if any(rep.time == t for rep in a[t][1])][1::]))))} """
        return {t: r if t in b_relevant_keys else SemanticsUtils.create_empty_result(b) for (t, r) in b.items()}
