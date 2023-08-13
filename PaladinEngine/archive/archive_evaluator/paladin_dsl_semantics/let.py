import ast
from typing import Iterable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time
from archive.archive_evaluator.paladin_dsl_semantics.operator import Operator, BiLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.pure_eval_once import _PureEvalOnce
from ast_common.ast_common import ast2str


class Let(BiLateralOperator):
    BOUND_ARG_INDEX = 0
    LET_BOUNDED_KEY = 'BOUNDED'

    def __init__(self, times: Iterable[Time], first: str, second: Operator):
        super().__init__(times, _PureEvalOnce(times, first), second)

    def eval(self, eval_data) -> EvalResult:
        return self.second.eval(eval_data)

    @classmethod
    def is_let(cls, node: ast.AST):
        return isinstance(node, ast.Call) and ast2str(node.func) == cls.__name__
