from typing import Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.selector_op import Selector
from archive.object_builder.object_builder import ObjectBuilder


class Old(UniLateralOperator, Selector):
    """
        Old(o): Retrieves the previous value of o, i.e. (0:None, 1:o(0), 2:o(1)...)
    """
    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:

        if str(self.first) in query_locals:
            first = query_locals[str(self.first)]
        else:
            first = self.first.eval(builder, query_locals, user_aux)

        return EvalResult([EvalResultEntry.empty_with_keys(0, first.all_keys())] + [
            EvalResultEntry(e.time + 1, e.evaled_results, []) for e in list(first)
        ])
