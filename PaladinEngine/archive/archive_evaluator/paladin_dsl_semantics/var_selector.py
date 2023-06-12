from typing import Iterable, Optional, Dict, Tuple

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry, \
    EvalResultPair, LineNo
from archive.archive_evaluator.paladin_dsl_semantics import Const
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator, Operator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time
from archive.object_builder.diff_object_builder.diff_object_builder import DiffObjectBuilder
from archive.object_builder.object_builder import ObjectBuilder


class VarSelector(UniLateralOperator):

    VARS_KEY = 'vars'

    def __init__(self, times: Iterable[Time], first: Operator):
        UniLateralOperator.__init__(self, times, first)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None):
        return EvalResult([
            EvalResultEntry(t, [
                EvalResultPair(VarSelector.VARS_KEY, self._get_all_vars(builder, time_range))], [])
            for time_range in self.first.eval(builder, query_locals).satisfaction_ranges(self.times) for t in time_range
        ])

    def _get_assignments(self, builder: ObjectBuilder, time_range: range):
        return builder.archive.get_assignments(time_range=time_range)

    def _get_all_vars(self, builder: ObjectBuilder, time_range: range) -> Dict[Tuple[str, LineNo], Iterable[Time]]:
        res = {}
        for k, vv in self._get_assignments(builder, time_range):
            res_key = vv.expression, self._get_line_no(builder, vv.expression, vv.key.container_id)
            if res_key not in res:
                res[res_key] = []
            res[res_key].append(vv.time)
        return res

    def _get_line_no(self, builder: ObjectBuilder, expr: str, container_id: int) -> LineNo:
        return -1


class VarSelectorByTimeAndLines(VarSelector):
    def __init__(self, times: Iterable[Time], time: Operator, lines: range):
        super().__init__(times, time)
        self.lines = lines

    def _get_assignments(self, builder: ObjectBuilder, time_range: range):
        return builder.archive.get_assignments(time_range=time_range, line_nos=self.lines)

    def _get_line_no(self, builder: ObjectBuilder, expr: str, container_id: int) -> LineNo:
        return builder.get_line_no_by_name_and_container_id(expr, container_id)


class VarSelectorByLineNo(VarSelectorByTimeAndLines):
    def __init__(self, times: Iterable[Time], time: Operator, line_no: LineNo):
        super().__init__(times, time, range(line_no, line_no + 1))
        self.line_no: LineNo = line_no

    def _get_assignments(self, builder: ObjectBuilder, time_range: range):
        if not isinstance(builder, DiffObjectBuilder):
            return []
        return builder.archive.get_assignments(time_range, line_nos=builder.get_line_nos_by_container_ids(
            builder.get_container_ids_by_line_no(self.line_no)))
