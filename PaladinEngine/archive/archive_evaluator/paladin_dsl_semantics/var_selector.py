from typing import Iterable, Optional, Dict, Tuple, Callable, List

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry, \
    EvalResultPair, LineNo
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator, Operator
from archive.archive_evaluator.paladin_dsl_semantics.selector_op import Selector
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time, TRUE
from archive.object_builder.diff_object_builder.diff_object_builder import DiffObjectBuilder
from archive.object_builder.object_builder import ObjectBuilder
from ast_common.ast_common import deconstruct


class VarSelector(UniLateralOperator, Selector):
    VARS_KEY = 'vars'

    def __init__(self, times: Iterable[Time], first: Operator):
        UniLateralOperator.__init__(self, times, first)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        return EvalResult([
            EvalResultEntry(t, [
                EvalResultPair(VarSelector.VARS_KEY, self._get_all_vars(builder, time_range))], [])
            for time_range in self.first.eval(builder, query_locals, user_aux).satisfaction_ranges(self.times) for t in
            time_range
        ])

    def _get_assignments(self, builder: ObjectBuilder, time_range: range):
        return builder.archive.get_assignments(time_range=time_range)

    def _get_all_vars(self, builder: ObjectBuilder, time_range: range) -> Dict[Tuple[str, LineNo], Iterable[Time]]:
        res = {}
        for k, vv in filter(lambda t: not t[1].expression.startswith('__'), self._get_assignments(builder, time_range)):
            base, attr, _ = deconstruct(vv.expression)
            if attr != '':
                # Attributes.
                var_name = f'{base}.{attr}'
                #base_container_id = VarSelector._get_parent_container_id(vv, builder)
                res_key = var_name, -1
            else:
                res_key = base, self._get_line_no(builder, vv, expr=base)
            if res_key not in res:
                res[res_key] = []
            res[res_key].append(vv.time)
        return res

    def _get_line_no(self, builder: ObjectBuilder, vv: Archive.Record.RecordValue, expr: str = None) -> LineNo:
        return -1

    @staticmethod
    def _get_parent_container_id( v: Archive.Record.RecordValue, builder: ObjectBuilder):
        container_ids = set(map(lambda t: t[0].container_id,
                            builder.archive.flatten_and_filter(lambda vv: vv.value == v.key.container_id)))

        if len(container_ids) != 1:
            raise RuntimeError("...")

        return container_ids.pop()



class _VarSelectorByEntries(VarSelector):

    def __init__(self, times: Iterable[Time],
                 entries: List[Tuple[Archive.Record.RecordKey, Archive.Record.RecordValue]]):
        super().__init__(times, TRUE(times))
        self.assignments = entries

    def _get_assignments(self, builder: ObjectBuilder, time_range: range):
        return filter(lambda t: t[0].kind == Archive.Record.StoreKind.VAR, self.assignments)

    def _get_line_no(self, builder: ObjectBuilder, vv: Archive.Record.RecordValue, expr: str = None) -> LineNo:
        return vv.line_no


class VarSelectorByTimeAndLines(VarSelector):
    def __init__(self, times: Iterable[Time], time: Operator, lines: range):
        super().__init__(times, time)
        self.lines = lines

    def _get_assignments(self, builder: ObjectBuilder, time_range: range):
        return builder.archive.get_assignments(time_range=time_range, line_nos=self.lines)

    def _get_line_no(self, builder: ObjectBuilder, vv: Archive.Record.RecordValue, expr: str = None) -> LineNo:
        return builder.get_line_no_by_name_and_container_id(expr if expr else vv.expression, vv.key.container_id)


class VarSelectorByLineNo(VarSelectorByTimeAndLines):
    def __init__(self, times: Iterable[Time], time: Operator, line_no: LineNo):
        super().__init__(times, time, range(line_no, line_no + 1))
        self.line_no: LineNo = line_no

    def _get_assignments(self, builder: ObjectBuilder, time_range: range):
        if not isinstance(builder, DiffObjectBuilder):
            return []
        return builder.archive.get_assignments(time_range, line_nos=builder.get_line_nos_by_container_ids(
            builder.get_container_ids_by_line_no(self.line_no)))
