from types import NoneType
from typing import Iterable, Optional, Dict, Callable, Type

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Time, EvalResult, EvalResultEntry, \
    EvalResultPair, LineNo, EVAL_BUILTIN_CLOSURE
from archive.archive_evaluator.paladin_dsl_semantics import Raw
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator, Operator
from archive.archive_evaluator.paladin_dsl_semantics.selector_op import Selector
from archive.object_builder.object_builder import ObjectBuilder
from common.common import ISP


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
        if ISP(type(self.first)):
            return EvalResult.create_const(self.times, Type.TYPE_KEY, type(self.first).__name__)
        elif isinstance(self.first, Raw):
            name = self.first.query
        else:
            return EvalResult.empty(self.times)

        return EvalResult(
            [
                EvalResultEntry(t, [
                    EvalResultPair(Type.TYPE_KEY, self.get_type(builder, query_locals, user_aux, name, t))], [])
                for t in self.times
            ]
        )

    def get_type(self, builder: ObjectBuilder, query_locals, user_aux, e: str, t: Time) -> Optional[str]:
        # Try to evaluate in case that name is actually an expression.
        try:
            return eval(f'type({e}).__name__', EVAL_BUILTIN_CLOSURE)
        except NameError:
            pass

        # Try to treat e as a variable name and find it in the builder.
        _type = builder.get_type(e, t, self.line_no)
        if _type is not NoneType:
            return _type.__name__

        # Try to evaluate it through a normal builder-build.

        r = Raw(e, line_no=self.line_no, times=[t]).eval(builder, query_locals, user_aux).first_satisfaction()
        if len(r) == 0:
            return None

        return type(r[e].value).__name__


