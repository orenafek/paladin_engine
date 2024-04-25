import ast
from typing import Optional, Dict, Iterable, Any, cast, Callable

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, Time
from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import FUNCTION_CALL_MAGIC
from archive.archive_evaluator.paladin_dsl_semantics.operator import UniLateralOperator
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.archive_evaluator.paladin_dsl_semantics.time_operator import TimeOperator
from archive.object_builder.object_builder import ObjectBuilder
from ast_common.ast_common import str2ast


class Changed(UniLateralOperator, TimeOperator):
    """
    Changed(e/e@ln): Satisfied for each time in which e has been changed,
                     either assigned to or internally (as for objects).
    """

    def __init__(self, times: Iterable[Time], first: Raw):
        UniLateralOperator.__init__(self, times, first)
        TimeOperator.__init__(self, times)

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        if not isinstance(self.first, Raw):
            return EvalResult.empty(self.times)

        res = self.first.eval(builder, query_locals, user_aux)
        not_none_times = [i.time for i in res if not all(x is None for x in i.values)]

        if len(res) == 0 or not not_none_times:
            return EvalResult.empty(self.times)

        res_iter = iter(filter(lambda i: i.time in not_none_times, res))
        last = next(res_iter)
        change_times = [not_none_times[0]]
        for curr in res_iter:
            if curr.items != last.items:
                change_times.append(curr.time)

            last = curr

        return EvalResult([
            TimeOperator.create_time_eval_result_entry(t, t in change_times, []) for t in self.times
        ])

    @staticmethod
    def separate(expr: str):
        magic_value = '__XX__'
        if FUNCTION_CALL_MAGIC in expr:
            expr = expr.replace(FUNCTION_CALL_MAGIC, magic_value)

        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self.components = []

            def visit_Name(self, node: ast.Name) -> Any:
                if magic_value in node.id:
                    name = node.id.strip()
                else:
                    name = node.id

                self.components.append(name)

            def visit_Attribute(self, node: ast.Attribute) -> Any:
                self.visit(cast(ast.AST, node.value))
                self.components.append(node.attr)

        visitor = Visitor()
        visitor.visit(str2ast(expr))
        return visitor.components
