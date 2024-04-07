import ast
import json
import traceback
from _ast import BinOp, AST
from collections import deque
from dataclasses import dataclass
from typing import *  # DO NOT REMOVE!!!!

from common.attributed_dict import AttributedDict
from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, BAD_JSON_VALUES, \
    EVAL_BUILTIN_CLOSURE, BUILTIN_SPECIAL_FLOATS, Time, ParseResults
from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import FUNCTION_CALL_MAGIC
from archive.archive_evaluator.paladin_dsl_semantics import Const
from archive.archive_evaluator.paladin_dsl_semantics.operator import Operator
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.object_builder.diff_object_builder.diff_object_builder import DiffObjectBuilder
from archive.object_builder.object_builder import ObjectBuilder
from ast_common.ast_common import ast2str, str2ast, is_tuple, split_tuple
from finders.finders import GenericFinder, StubEntry, ContainerFinder
from stubbers.stubbers import Stubber


class PaladinNativeParser(object):
    Customizer: Type = Callable[[Dict], Dict]
    SCOPE_SIGN_OPERATOR = ast.MatMult  # @
    OPERATORS: Dict[str, Union[Type[Operator], Type[Operator]]] = {op.name(): op for op in
                                                                   Operator.all()}
    FUNCTION_CALL_MAGIC = '$'
    _FUNCTION_CALL_MAGIC_REPLACE_SYMBOL = '__FC_RET_VAL__'
    _COMPREHENSION_MAGIC_REPLACE_SYMBOL = '__COMP_SYMBOL__'

    def __init__(self, archive: Archive, object_builder_type: Type = DiffObjectBuilder,
                 should_time_builder_construction: bool = False):
        self.archive: Archive = archive
        self._line_no: int = -1
        self.builder: ObjectBuilder = object_builder_type(archive, should_time_builder_construction)
        self.construction_time = self.builder.construction_time
        self.user_aux: Dict[str, Any] = {}

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
            if not self.operators or not isinstance(visit_result, ast.Name):
                if isinstance(node, ast.Expr) and node.lineno != node.value.lineno:
                    node.lineno = node.value.lineno
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

            return ast.Name(id=var_name, lineno=node.lineno)

        def visit_Slice(self, node: ast.Slice) -> Any:
            parts = []
            for part in [node.lower, node.upper, node.step]:
                if part is None:
                    parts.append(part)
                    continue
                part_visit_result = self.visit(part)
                if isinstance(part_visit_result, ast.Constant):
                    parts.append(part_visit_result.value)
                    continue

                var_name = self.create_operator_lambda_var()
                self._add_operator(var_name, ast2str(part), Raw(ast2str(part_visit_result), part.lineno, self.times))
                parts.append(ast.Attribute(value=ast.Name(id=var_name), attr=ast2str(part)))

            return ast.Slice(lower=parts[0], upper=parts[1], step=parts[2])

        def visit_Dict(self, node: ast.Dict) -> Any:
            return ast.Call(func=ast.Name(id=AttributedDict.__name__), args=[node], keywords=[], lineno=node.lineno)

        def _create_raw_op_from_arg(self, arg: ast.AST):
            return Raw(ast2str(arg), arg.lineno, self.times)

        def _create_const_op_from_arg(self, arg: ast.AST):
            return Const(ast2str(arg), self.times)

        def visit_Compare(self, node: ast.Compare) -> Any:
            node.left = super().visit(node.left)
            line_no = node.left.lineno
            for comp in node.comparators:
                comp = super().visit(comp)
                if line_no != -1 and comp.lineno != -1 and comp.lineno != line_no:
                    # In case line_no is already a real line no (not -1), and one of the comparators has a line_no,
                    # ignore all line_nos to not enforce the wrong line_no from both sides or cross-comparators.
                    line_no = -1
                elif line_no == -1 and comp.lineno != -1:
                    # If there is no line_no yet, take the comp's one.
                    line_no = comp.lineno

            node.lineno = line_no
            return node

        def visit_Name(self, node: ast.Name) -> Any:
            if PaladinNativeParser._FUNCTION_CALL_MAGIC_REPLACE_SYMBOL in node.id:
                name = node.id.replace(PaladinNativeParser._FUNCTION_CALL_MAGIC_REPLACE_SYMBOL, '')
            elif PaladinNativeParser._COMPREHENSION_MAGIC_REPLACE_SYMBOL in node.id:
                name = node.id.replace(PaladinNativeParser._COMPREHENSION_MAGIC_REPLACE_SYMBOL, '')
            else:
                name = node.id

            if name != node.id:
                var_name = self.create_operator_lambda_var()
                self._add_operator(var_name, name, Raw(name, node.lineno, self.times))
                name = var_name

            return ast.Name(id=name, lineno=node.lineno)

        def visit_Attribute(self, node: ast.Attribute) -> Any:
            if PaladinNativeParser._COMPREHENSION_MAGIC_REPLACE_SYMBOL in node.attr:
                node.attr = node.attr.replace(PaladinNativeParser._COMPREHENSION_MAGIC_REPLACE_SYMBOL, '')
            super().visit(node.value)
            node.lineno = node.value.lineno
            return node

        def visit_comprehension(self, node: ast.comprehension) -> Any:
            if not (isinstance(node.iter, ast.Call) and PaladinNativeParser.OperatorLambdaReplacer._is_operator_call(
                    node.iter)):
                class _Visitor(ast.NodeVisitor):
                    def visit_Name(self, _node: ast.Name) -> Any:
                        _node.id = PaladinNativeParser._COMPREHENSION_MAGIC_REPLACE_SYMBOL + _node.id

                    def visit_Attribute(self, _node: ast.Attribute) -> Any:
                        _node.attr = PaladinNativeParser._COMPREHENSION_MAGIC_REPLACE_SYMBOL + _node.attr

                _Visitor().visit(cast(ast.AST, node.iter))

            node.iter = super().visit(cast(ast.AST, node.iter))
            node.target = super().visit(cast(ast.AST, node.target))
            return node

        @staticmethod
        def _is_operator_call(node: ast.Call):
            return isinstance(node.func, ast.Name) and Operator.is_operator(node.func.id)

        @property
        def _seed(self):
            self._lambda_var_seed += 1
            return self._lambda_var_seed

        def create_operator_lambda_var(self) -> str:
            return f'__O{self._seed}'

        def _add_operator(self, var_name: str, original_op: str, op: Operator):
            self.operators[var_name] = op, original_op
            self.root_vars.append(var_name)

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

    def json_dumps(self, obj: Any):
        # noinspection PyMethodParameters
        class _encoder(json.JSONEncoder):

            def __init__(_self, *, skipkeys: bool = ..., ensure_ascii: bool = ..., check_circular: bool = ...,
                         allow_nan: bool = ..., sort_keys: bool = ..., indent: int | None = ...,
                         separators: tuple[str, str] | None = ..., default: Callable[..., Any] | None = ...) -> None:
                super().__init__(skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                                 allow_nan=allow_nan, sort_keys=sort_keys, indent=indent, separators=separators,
                                 default=default)
                _self.nan_str = 'NaN'

            def default(_self, o: Any) -> Any:
                if any([isinstance(o, t) for t in {set, deque}]):
                    return list(o)

                if isinstance(o, float) and o in BUILTIN_SPECIAL_FLOATS.values():
                    return str(super().default(o))

                return super().default(o)

            def iterencode(_self, o: Any, _one_shot=False) -> Iterator[str]:
                # noinspection PyMethodParameters
                class Tuple2StrReplacer(ast.NodeTransformer):
                    def visit_Dict(_self, node: ast.Dict) -> Any:
                        # noinspection PyTypeChecker
                        node.keys = [
                            ast.Constant(value=ast2str(k)) if isinstance(k, ast.Tuple) or isinstance(k, ast.Dict) else k
                            for k in node.keys
                        ]
                        return _self.generic_visit(node)

                    def visit_Set(self, node: ast.Set) -> Any:
                        return ast.List(elts=node.elts)

                return super().iterencode(
                    eval(ast2str(Tuple2StrReplacer().visit(str2ast(str(o))), _one_shot), EVAL_BUILTIN_CLOSURE))

        return PaladinNativeParser._remove_bad_json_values(json.dumps(obj, cls=_encoder))

    def parse(self, query: str, start_time: int, end_time: int, jsonify: bool = True, customizer: str = '') -> \
            Union[str, EvalResult]:
        try:
            times = range(start_time, end_time + 1)

            # Handle function call magic symbols.
            query = PaladinNativeParser.__replace_function_call_magic(query)

            query_ast = str2ast(query.strip().replace('\n', ' '))

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
                query, results = PaladinNativeParser._restore_original_operator_keys(query_ast, visitor, query_result)

            elif not query_result:
                if jsonify:
                    return self.json_dumps(EvalResult.empty(times))
                return EvalResult.empty(times)

            results = EvalResult(results)
            if not jsonify:
                return results

            grouped = results.group()

            if customizer != '':
                grouped = PaladinNativeParser.customize(customizer, grouped)

            # Add the keys in the first row.
            # noinspection PyTypeChecker
            grouped['keys'] = list(results.all_keys())

            # Remove bad JSON values.
            return self.json_dumps(grouped)

        except BaseException as e:
            traceback.print_exc()
            if jsonify:
                return json.dumps("")

            raise e

    def add_user_aux(self, f_content: str | bytes):
        exec(f_content, self.user_aux)

    def remove_user_aux(self):
        self.user_aux.clear()

    def _eval_operators(self, visitor):
        operator_results = {}
        for var_name, (operator, operator_original_name) in visitor.operators.items():
            eval_result = operator.eval(self.builder, operator_results, self.user_aux)
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
    def _restore_original_operator_keys(query_ast: ast.AST, visitor: OperatorLambdaReplacer, result: EvalResult) -> \
            Tuple[str, EvalResult]:
        for var_name, (operator, operator_original_name) in reversed(visitor.operators.items()):
            result = EvalResult.rename_key(result, operator_original_name, var_name)

        return visitor.operators[ast2str(query_ast)][1], result

    @classmethod
    def _remove_bad_json_values(cls, json_string: str):
        for bad_json_word in BAD_JSON_VALUES:
            json_string = json_string.replace(str(bad_json_word), BAD_JSON_VALUES[str(bad_json_word)])

        return json_string

    @staticmethod
    def __replace_function_call_magic(query: str) -> str:
        if PaladinNativeParser._FUNCTION_CALL_MAGIC_REPLACE_SYMBOL in query:
            raise RuntimeError('Secret magic found in query :(')

        return query.replace(FUNCTION_CALL_MAGIC, PaladinNativeParser._FUNCTION_CALL_MAGIC_REPLACE_SYMBOL)

    @staticmethod
    def customize(customizer_str: str, results: ParseResults) -> ParseResults:
        try:
            exec(customizer_str)
            customizer_func: PaladinNativeParser.Customizer = locals()[
                'customizer'] if 'customizer' in locals() else None
            # Customize.
            return {k: customizer_func(v) for k, v in results.items()} if customizer_func else results
        except BaseException as e:
            traceback.print_exception(e)

    @classmethod
    def docs(cls):
        return '```' '\n' + '\n'.join(
            sorted([op.__doc__.strip() for op in Operator.all() if op.__doc__])) + '\n' + '```'
