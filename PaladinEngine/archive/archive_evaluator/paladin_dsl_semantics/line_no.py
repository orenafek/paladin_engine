from typing import Optional, Dict

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry, \
    EvalResultPair
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class LineNo(UniLateralOperator):
    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None) -> EvalResult:
        evaled = self.first.eval(builder, query_locals)

        return EvalResult(
            [EvalResultEntry(e.time, [EvalResultPair('LineNo', builder.get_line_nos_for_time(e.time) if e.satisfies() else [])], []) for e in
             evaled ])
