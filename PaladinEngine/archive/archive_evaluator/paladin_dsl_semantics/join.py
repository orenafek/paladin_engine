from typing import Iterable, Optional, Dict, Callable, cast

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult, EvalResultEntry, \
    EvalResultPair
from archive.archive_evaluator.paladin_dsl_semantics import Operator
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.archive_evaluator.paladin_dsl_semantics.const import Const
from archive.archive_evaluator.paladin_dsl_semantics.operator import VariadicLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Join(VariadicLateralOperator):
    def __init__(self, times: Iterable[Time], *args: Operator):
        super().__init__(times, *args)
        if not (5 <= len(args) <= 6):
            raise RuntimeError('inappropriate syntax for Join')

        self.to_eval: Operator = args[0]
        self.iter1: str = cast(Raw, args[1]).query
        self.col1: Operator = args[2]
        self.iter2: str = cast(Raw, args[3]).query
        self.col2: Operator = args[4]
        self.cond: Operator = args[5] if len(args) == 6 else Const(True, self.times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        first_col = self.col1.eval(builder, query_locals, user_aux)
        second_col = self.col2.eval(builder, query_locals, user_aux)
        joined_locals = self._query_locals_for_joined(query_locals, first_col, self.iter1, second_col, self.iter2)
        cond_times = self.cond.eval(builder, joined_locals, user_aux).satisfaction_times()

        self.to_eval.update_times(cond_times)
        return self.to_eval.eval(builder, joined_locals, user_aux)

    def _query_locals_for_joined(self, query_locals: Optional[Dict[str, EvalResult]], c1: EvalResult, var1: str,
                                 c2: EvalResult, var2: str):
        return {**query_locals, **self._rename_result(c1, var1), **self._rename_result(c2, var2)}

    def _rename_result(self, r: EvalResult, v: str):
        return {v: EvalResult([EvalResultEntry(t, [EvalResultPair(k, v) for k, v in r[t].items]) for t in self.times])}


# Join((e1.total_slices, {e2.total_slices}),
#      e1, Where(Union(total_slices@26, i@25, j@25), LineHit(30)),
#      e2, Where(Union(total_slices@12, i@13, j@14), LineHit(16)),
#      (e1.i == e2.i and e1.j and (e1.j + 1 == e2.j))
#      )
