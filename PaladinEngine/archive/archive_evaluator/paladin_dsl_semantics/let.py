from typing import Optional, Dict, Callable, Iterable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time
from archive.archive_evaluator.paladin_dsl_semantics.aux_op import AuxOp
from archive.archive_evaluator.paladin_dsl_semantics.operator import Operator, VariadicLateralOperator
from archive.object_builder.object_builder import ObjectBuilder


class Let(VariadicLateralOperator, AuxOp):
    """
        Let(a1:=e1, a2:=e2, ...an:=en, o): Runs o with a1,...an as aliases to e1,...en respectfully.
    """
    LET_BOUNDED_KEY = 'BOUNDED'

    def __init__(self, times: Iterable[Time], *args: Operator, **kwargs: Operator):
        if len(args) != 1:
            raise SyntaxError('Only one non-var binding operand is permitted')
        parallel = kwargs.pop('parallel', False)
        super().__init__(times, *args, **kwargs)
        self.expr = args[0]
        self.vars = kwargs

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None) -> EvalResult:

        let_locals = query_locals
        for var_name, var_op in self.vars.items():
            var_res = var_op.eval(builder, let_locals, user_aux)
            if len(keys := list(var_res.all_keys())) > 1:
                raise SyntaxError('bounded expressions can\'t be tuples')
            let_locals = self._update_locals(let_locals, var_name, keys[0], var_res)
        return self.expr.eval(builder, let_locals, user_aux)

    def _update_locals(self, query_locals, v: str, orig_key: str, res: EvalResult) -> Dict[str, EvalResult]:
        EvalResult.rename_key(res, v, orig_key)
        return {**query_locals, v: res}
