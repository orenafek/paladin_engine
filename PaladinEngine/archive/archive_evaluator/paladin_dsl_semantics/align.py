from dataclasses import dataclass
from typing import Callable, Optional, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult
from archive.archive_evaluator.paladin_dsl_semantics.operator import BiLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import SemanticsUtils
from archive.object_builder.object_builder import ObjectBuilder


class Align(BiLateralOperator):
    """
        Align(<c1>, <c2>): Selects <c1> and <c2> by aligning them using heuristics.
    """

    @dataclass
    class AlignmentHeuristic(object):
        func: Callable
        pattern: str

        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs), self.pattern

    ALIGNMENT_HEURISTICS = [
        AlignmentHeuristic(lambda r1, r2: lambda r: r, 'r -> r'),
        AlignmentHeuristic(lambda r1, r2: lambda r: r - (r2 - r1), 'r - r1'),
        AlignmentHeuristic(lambda r1, r2: lambda r: r * (r2 / r1), 'r * (r / r1)')
    ]

    def __init__(self):
        super(BiLateralOperator, self).__init__()

        self._heuristic_iterator = iter(Align.ALIGNMENT_HEURISTICS)
        self._current_heuristic = None

    def next_heuristic(self, r1, r2):
        if self._current_heuristic != Align.ALIGNMENT_HEURISTICS[1]:
            self._current_heuristic = next(self._heuristic_iterator)

        return self._current_heuristic(r1, r2)

    def eval(self, eval_data):
        r1 = self.first.eval(eval_data)
        r2 = self.second.eval(eval_data)

        if isinstance(r1, bool) or isinstance(r2, bool):
            raise TypeError("Cannot run Align if any of its operands are bool.")

        r1_selectors, r2_selectors = SemanticsUtils.selectors(r1), SemanticsUtils.selectors(r2)

        all_selectors = list(r1_selectors) + list(r2_selectors)
        results = {k: ({k: None for k in all_selectors}, []) for k in SemanticsUtils.joined_times(r1, r2)}

        r1_clipped = SemanticsUtils.remove_none_prefix(r1)
        r2_clipped = SemanticsUtils.remove_none_prefix(r2)

        heuristic, heuristic_pattern = self.next_heuristic(None, None)

        for s1, s2 in zip(r1_selectors, r2_selectors):
            assert SemanticsUtils.extract_name(s1) == SemanticsUtils.extract_name(s2)
            for t1, t2 in zip(r1_clipped, r2_clipped):
                res1 = r1[t1][0][s1]
                res2 = heuristic(r2[t2][0][s2])
                updated_results = {s1: res1, s2: res2}

                # The values are the same.
                if res1 != res2:
                    # There is a difference between the values of the selector of r1 and r2.
                    # Create a heuristic with both values.
                    heuristic, heuristic_pattern = self.next_heuristic(res1, res2)
                    updated_results[SemanticsUtils.replace_selector_name(s2, heuristic_pattern)] = heuristic(res2)

                results[t1][0].update(**updated_results)
                results[t1][1].extend(set(results[t1][1]).union(r1[t1][1]).union(r2[t1][1]))

        return results
