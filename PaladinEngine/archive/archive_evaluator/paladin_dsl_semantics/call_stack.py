from typing import Optional, Dict, Callable, Iterable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry, \
    EvalResultPair, Time
from archive.archive_evaluator.paladin_dsl_semantics import Operator
from archive.archive_evaluator.paladin_dsl_semantics.operator import OptionalArgOperator
from archive.object_builder.object_builder import ObjectBuilder


class CallStack(OptionalArgOperator):
    """
       CallStack():  Retrieves all function calls in the program run.
    """
    CALLER_KEY = 'Caller'
    CALLEE_KEY = 'Callee'

    def __init__(self, times: Iterable[Time], include_builtins: Optional[bool] = True):
        super().__init__(times, None)
        self.include_builtins = include_builtins

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:
        call_chain = builder.get_call_chain(self.include_builtins)
        return EvalResult([
            EvalResultEntry(t, [EvalResultPair(CallStack.CALLER_KEY, call_chain[t][0]),
                                EvalResultPair(CallStack.CALLEE_KEY, call_chain[t][1])]) if t in call_chain
            else EvalResultEntry.empty(t) for t in self.times
        ])
