from typing import Iterable, Optional, Dict, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult, EvalResultEntry, \
    EvalResultPair, LineNo
from archive.archive_evaluator.paladin_dsl_semantics import Const, Raw
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator, Operator
from archive.archive_evaluator.paladin_dsl_semantics.selector_op import Selector
from archive.object_builder.object_builder import ObjectBuilder


class Type(UniLateralOperator, Selector):
    """
    Type(var/var@ln): Retrieve the type of the variable(s) named var from the log.
    """
    TYPE_KEY = "Type"

    def __init__(self, times: Iterable[Time], name: Operator, line_no: LineNo = -1):
        super().__init__(times, name)
        self.line_no = line_no

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        if not isinstance(self.first, Raw):
            return EvalResult.empty(self.times)

        name = self.first.query
        return EvalResult([EvalResultEntry(t,
                                           [EvalResultPair(Type.TYPE_KEY,
                                                           builder.get_type(name, t, self.line_no).__name__)
                                            ], []) for t in self.times])
