from typing import Iterable, Optional, Dict

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry, \
    EvalResultPair
from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import SCOPE_SIGN
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator, Operator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time
from archive.object_builder.object_builder import ObjectBuilder


class VarSelector(UniLateralOperator):
    """
        VarSelector(<time_range>): Selects all vars that were changed in a time range.
    """

    VARS_KEY = 'vars'

    def __init__(self, times: Iterable[Time], first: Operator):
        UniLateralOperator.__init__(self, times, first)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        return EvalResult([
            EvalResultEntry(t, [
                EvalResultPair(VarSelector.VARS_KEY, self._get_all_vars(builder, time_range))], [])
            for time_range in self.first.eval(builder, query_locals).satisfaction_ranges(self.times) for t in time_range
        ])

    def _get_assignments(self, builder: Archive, time_range: range):
        return builder.get_assignments(time_range=time_range)

    def _get_all_vars(self, builder: ObjectBuilder, time_range: range) -> Iterable[str]:
        return {f'{vv.expression}{SCOPE_SIGN}-1' for k, vv in self._get_assignments(builder.archive, time_range)}


class VarSelectorByTimeAndLines(VarSelector):
    def __init__(self, times: Iterable[Time], time: Operator, lines: range):
        super().__init__(times, time)
        self.lines = lines

    def _get_assignments(self, builder: Archive, time_range: range):
        return builder.get_assignments(time_range=time_range, line_no_range=self.lines)

    def _get_all_vars(self, builder: ObjectBuilder, time_range: range) -> Iterable[str]:
        res = set()
        for k, vv in self._get_assignments(builder.archive, time_range):
            all_line_no_of_name = builder.get_line_nos_from_name(vv.expression)
            if not all_line_no_of_name:
                line_no = -1
            else:
                line_no_in_range = filter(lambda ln: ln in self.lines, all_line_no_of_name)
                if not line_no_in_range:
                    line_no = -1
                else:
                    line_no = next(line_no_in_range)

            res.add(f'{vv.expression}{SCOPE_SIGN}{line_no}')

        return res
