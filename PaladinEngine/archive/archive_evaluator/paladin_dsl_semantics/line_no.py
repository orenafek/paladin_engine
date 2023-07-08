from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry, \
    EvalResultPair
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class LineNo(UniLateralOperator):
    """
    LineNo(o): Retrieve the line numbers in the program for each event that had happened in the entry's time if it has been satisfied.
    """

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        evaled = self.first.eval(builder, query_locals, user_aux)

        return EvalResult(
            [EvalResultEntry(e.time,
                             [EvalResultPair('LineNo', builder.get_line_nos_for_time(e.time) if e.satisfies() else [])],
                             []) for e in
             evaled])
