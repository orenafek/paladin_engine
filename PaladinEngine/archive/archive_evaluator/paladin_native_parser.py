import ast
import json
from _ast import BinOp, AST
from dataclasses import dataclass
from typing import *

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EvalResultEntry, \
    EvalResultPair
from archive.archive_evaluator.paladin_dsl_semantics import Operator, Time, Raw
from ast_common.ast_common import ast2str, str2ast, is_tuple, split_tuple
from finders.finders import GenericFinder, StubEntry, ContainerFinder
from stubbers.stubbers import Stubber


class PaladinNativeParser(object):
    SCOPE_SIGN_OPERATOR = ast.MatMult  # @
    OPERATORS: Dict[str, Union[Type[Operator], Type[Operator]]] = {op.name(): op for op in
                                                                   Operator.all()}

    def __init__(self, archive: Archive):
        self.archive = archive
        self._line_no = -1

    class HasOperatorVisitor(ast.NodeVisitor):
        def visit(self, node: ast.AST):
            return bool(super().visit(node))

        def generic_visit(self, node):
            """Called if no explicit visitor function exists for a node."""
            for field, value in ast.iter_fields(node):
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, ast.AST):
                            if self.visit(item):
                                return True
                elif isinstance(value, ast.AST):
                    if self.visit(value):
                        return True

        def visit_Call(self, node: ast.Call) -> Any:
            return PaladinNativeParser._is_operator_call(node)

        def visit_BinOp(self, node: ast.BinOp) -> Any:
            return True

    class LineNumberReplacer(ast.NodeTransformer):
        def __init__(self):
            super().__init__()
            self.line_no = -1

        def visit(self, node: AST) -> Any:
            result = super().visit(node)
            node.lineno = self.line_no
            return result

        def visit_BinOp(self, node: BinOp) -> Any:
            if not isinstance(node.op, PaladinNativeParser.SCOPE_SIGN_OPERATOR):
                return super().generic_visit(node)

            if not isinstance(node.right, ast.Constant):
                raise SyntaxError('The RHS of @ should be a positive integer.')

            # Set line no.
            self.line_no = node.right.value

            node.left.lineno = node.right.value

            return node.left

    class OperatorLambdaReplacer(ast.NodeTransformer):
        def __init__(self, times: Iterable[Time]):
            super().__init__()
            self.times: Iterable[Time] = times
            self._lambda_var_seed: int = -1
            self.operators: Dict[str, Tuple[Operator, str]] = {}
            self.root_vars = []
            self._visited_root: bool = False

        def visit(self, node: ast.AST) -> Any:
            if self._visited_root:
                return super().visit(node)

            self._visited_root = True
            visit_result = super().visit(node)
            if not self.operators:
                var_name = self.create_operator_lambda_var()
                self._add_operator(var_name, ast2str(node), Raw(ast2str(node), node.lineno, self.times))
                return ast.Name(id=var_name)

            return visit_result

        def visit_Call(self, node: ast.Call) -> Any:
            if not PaladinNativeParser._is_operator_call(node):
                return self.generic_visit(node)

            var_name = self.create_operator_lambda_var()
            # noinspection PyUnresolvedReferences,PyArgumentList,PyTypeChecker
            # Visit arguments.
            arg_vars = []
            for arg in node.args:
                arg_visit_result = self.visit(arg)
                if isinstance(arg_visit_result, ast.Name):
                    arg_vars.append(self.operators[arg_visit_result.id][0] if arg_visit_result.id in self.operators
                                    else self._create_raw_op_from_arg(arg_visit_result))
                elif isinstance(arg_visit_result, ast.Constant):
                    arg_vars.append(arg_visit_result.value)
                else:
                    arg_vars.append(self._create_raw_op_from_arg(arg_visit_result))

            # noinspection PyArgumentList,PyUnresolvedReferences
            self._add_operator(var_name, ast2str(node),
                               PaladinNativeParser.OPERATORS[node.func.id](self.times, *arg_vars))

            return ast.Name(id=var_name)

        def _create_raw_op_from_arg(self, arg: ast.AST):
            return Raw(ast2str(arg), arg.lineno, self.times)

        @property
        def _seed(self):
            self._lambda_var_seed += 1
            return self._lambda_var_seed

        def create_operator_lambda_var(self) -> str:
            return f'__O{self._seed}'

        def _add_operator(self, var_name: str, original_op: str, op: Operator):
            self.operators[var_name] = op, original_op
            self.root_vars.append(var_name)

        def update_query_locals(self):
            for operator in self.operators.values():
                if isinstance(operator, Raw):
                    operator.query_locals = self.operators

    class QueryVisitor(GenericFinder):

        @dataclass
        class OperatorLambdaExtra(object):
            operator: Operator
            op_var: str
            args_vars: Iterable[str]

        @dataclass
        class BinOpExtra(object):
            lhs_extra: object

        def __init__(self, parser: 'PaladinNativeParser', times: Iterable[Time], root: ast.AST):
            self.parser = parser
            self.times = times
            self.root = root
            self._lambda_var_seed = -1
            self.lambda_vars = set()
            self.operators_map = {}
            super().__init__()

        @property
        def _seed(self):
            self._lambda_var_seed += 1
            return self._lambda_var_seed

        def create_operator_lambda_var(self) -> str:
            return f'__O{self._seed}'

        def types_to_find(self) -> Union:
            return ast.Call

        def generic_visit(self, node: ast.AST) -> Any:
            has_operator = PaladinNativeParser.HasOperatorVisitor().visit(node)
            if not has_operator:
                return Raw(ast2str(node), node.lineno, self.times)

            visit_result = self.visit(node)
            if not visit_result:
                return self._get_visited_node_extra(node)

        def visit_Call(self, node: ast.Call) -> Any:
            if not PaladinNativeParser._is_operator_call(node):
                return self.generic_visit(node)

            # Visit call's arguments.
            args_extras = [self._visit_operator_arg(arg) for arg in node.args]
            args_for_operator = [
                extra if not isinstance(extra, PaladinNativeParser.QueryVisitor.OperatorLambdaExtra) else extra.operator
                for extra in args_extras
            ]
            args_vars = map(lambda ae: ae.args_vars, filter(
                lambda extra: isinstance(extra, PaladinNativeParser.QueryVisitor.OperatorLambdaExtra), args_extras))

            # noinspection PyUnresolvedReferences,PyArgumentList
            operator = PaladinNativeParser.OPERATORS[node.func.id](self.times, *args_for_operator)
            operator_lambda_var = self.create_operator_lambda_var()

            # Store the mapping of the operator to its var.
            self.operators_map[operator_lambda_var] = operator

            # return ast.Lambda(body=ast.Constant(id=operator_lambda_var), vars=ast.arguments(args=[ast.arg(arg=)]))
            # return ast.Constant(value=operator_lambda_var)
            return self._generic_visit_with_extras(node, PaladinNativeParser.QueryVisitor.OperatorLambdaExtra(
                operator, self.create_operator_lambda_var(), list(args_vars)))

        def _visit_operator_arg(self, arg: ast.AST):
            if isinstance(arg, ast.BinOp):
                return self.visit_BinOp(arg)

            visit_result = super(GenericFinder, self).visit(arg)

            # The visit has returned a direct object (most likely a Raw() object), pass it along.
            if visit_result:
                return visit_result

            # Return the extra object has been stored in the visit or none otherwise.
            return self._get_visited_node_extra(arg)

    def parse(self, query: str, start_time: int, end_time: int) -> str:

        try:
            times = range(start_time, end_time + 1)
            query_ast = str2ast(query.strip())

            # Propagate line numbers indicated by "@" scope.
            line_no_replacer = PaladinNativeParser.LineNumberReplacer()
            line_no_replacer.visit(query_ast)

            # Replace calling to operator with lambdas.
            visitor = PaladinNativeParser.OperatorLambdaReplacer(times)
            query_ast = visitor.visit(query_ast)

            # Evaluate operators.
            operator_results = self._eval_operators(visitor)

            # Evaluate the query.
            query_result = eval(ast2str(query_ast), operator_results)

            if isinstance(query_result, EvalResult):
                query_result = PaladinNativeParser._restore_original_operator_keys(visitor, query_result)

            results = [
                EvalResultEntry(t,
                                [EvalResultPair(k, v) for (k, v) in query_result[t].items()]
                                if isinstance(query_result[t], Dict)
                                else [EvalResultPair(query, query_result[t])], [])
                for t in times
            ]

            results = EvalResult(results)
            grouped = results.group()

            # Add the keys in the first row.
            grouped['keys'] = list(results.all_keys())

            return json.dumps(grouped)

        except BaseException as e:
            print(e)
            return json.dumps("")

    def _eval_operators(self, visitor):
        operator_results = {}
        for var_name, (operator, operator_original_name) in visitor.operators.items():
            eval_result = operator.eval(self.archive, operator_results)
            if is_tuple(var_name):
                operator_results.update({e: eval_result.by_key(e) for e in split_tuple(var_name)})
            else:
                operator_results[var_name] = eval_result

        # Evaluate query.
        return operator_results

    @staticmethod
    def _replace_operator_with_lambda_var(query_ast: ast.AST, stub_entry: StubEntry,
                                          lambda_operator_extra: 'PaladinNativeParser.QueryVisitor.OperatorLambdaExtra'):

        stub_record = Stubber.ReplacingStubRecord(stub_entry.node, stub_entry.container, stub_entry.attr_name,
                                                  replace=[ast.Name(id=lambda_operator_extra.op_var)])
        # replace=[ast.Name(id=v) for v in lambda_operator_extra.op_var])

        return Stubber(query_ast).stub(stub_record)

    @staticmethod
    def _replace_node_with_lambda(query_ast: ast.AST, node: ast.AST, lambda_vars: List[str]):
        finder = ContainerFinder(node)
        finder.visit(query_ast)
        if not finder.container:
            raise RuntimeError('Internal PaLaDiN Error :(')

        return Stubber(query_ast).stub(Stubber.ReplacingStubRecord(node, finder.container, finder.attr_name,
                                                                   replace=ast.Lambda(body=node,
                                                                                      args=[ast.Name(id=var) for var
                                                                                            in lambda_vars])))

    @staticmethod
    def _replace_bin_op_with_lhs(query_ast: ast.AST, stub_entry: StubEntry):
        stub_record = Stubber.ReplacingStubRecord(stub_entry.node, stub_entry.container, stub_entry.attr_name,
                                                  replace=stub_entry.extra)

        return Stubber(query_ast).stub(stub_record)

    @staticmethod
    def _is_operator_call(node: ast.Call) -> bool:
        return isinstance(node.func, ast.Name) and node.func.id in PaladinNativeParser.OPERATORS

    @property
    def line_no(self) -> int:
        return self._line_no

    @line_no.setter
    def line_no(self, value: int) -> None:
        self._line_no = value

    @staticmethod
    def _restore_original_operator_keys(visitor: OperatorLambdaReplacer, result: EvalResult) -> EvalResult:
        for var_name, (operator, operator_original_name) in visitor.operators.items():
            result.rename_key(var_name, operator_original_name)

        return result
