from typing import Iterable, Optional, Dict, Tuple

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry, \
    EvalResultPair, LineNo
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
        return {(vv.expression, -1) for k, vv in self._get_assignments(builder.archive, time_range)}


class VarSelectorByTimeAndLines(VarSelector):
    def __init__(self, times: Iterable[Time], time: Operator, lines: range):
        super().__init__(times, time)
        self.lines = lines

    def _get_assignments(self, builder: Archive, time_range: range):
        return builder.get_assignments(time_range=time_range, line_no_range=self.lines)

    def _get_all_vars(self, builder: ObjectBuilder, time_range: range) -> Iterable[Tuple[str, LineNo]]:
        return {
            (vv.expression, builder.get_line_no_by_name_and_container_id(vv.expression, vv.key.container_id))
            for k, vv in self._get_assignments(builder.archive, time_range)
        }
