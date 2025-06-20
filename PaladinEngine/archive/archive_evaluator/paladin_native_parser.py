import ast
import json
import re
import traceback
from _ast import BinOp, AST
from collections import deque
from dataclasses import dataclass
from typing import *  # DO NOT REMOVE!!!!

from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, BAD_JSON_VALUES, \
    EVAL_BUILTIN_CLOSURE, BUILTIN_SPECIAL_FLOATS, Time, EvalResultEntry
from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import FUNCTION_CALL_MAGIC
from archive.archive_evaluator.paladin_dsl_semantics import Const, TimeOperator
from archive.archive_evaluator.paladin_dsl_semantics.aux_op import AuxOp
from archive.archive_evaluator.paladin_dsl_semantics.for_each import ForEach
from archive.archive_evaluator.paladin_dsl_semantics.let import Let
from archive.archive_evaluator.paladin_dsl_semantics.old import Old
from archive.archive_evaluator.paladin_dsl_semantics.operator import Operator
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.archive_evaluator.paladin_dsl_semantics.selector_op import Selector
from archive.archive_evaluator.paladin_dsl_semantics.summary_op import SummaryOp
from archive.archive_evaluator.paladin_dsl_semantics.type_op import Type as TypeOp
from archive.object_builder.diff_object_builder.diff_object_builder import DiffObjectBuilder
from archive.object_builder.object_builder import ObjectBuilder
from ast_common.ast_common import ast2str, str2ast, is_tuple, split_tuple
from common.attributed_dict import AttributedDict
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
                 should_time_builder_construction: bool = False, parallel: bool = True):
        self.archive: Archive = archive
        self._line_no: int = -1
        self.builder: ObjectBuilder = object_builder_type(archive, should_time_builder_construction)
        self.construction_time = self.builder.construction_time
        self.user_aux: Dict[str, Any] = {}
        self.parallel = parallel

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
            node.left.ctx = '@'
            return node.left


    class OperatorLambdaReplacer(ast.NodeTransformer):
        def __init__(self, times: Iterable[Time], parallel: bool = True):
            super().__init__()
            self.times: Iterable[Time] = times
            self._lambda_var_seed: int = -1
            self.operators: Dict[str, Tuple[Operator, str]] = {}
            self.root_vars = []
            self._visited_root: bool = False
            self._extract_inner_ops: bool = True
            self.parallel = parallel

        def visit(self, node: ast.AST) -> Any:
            if self._visited_root:
                return super().visit(node)

            self._visited_root = True
            visit_result = super().visit(node)
            if not self.operators or not isinstance(visit_result, ast.Name):
                if isinstance(node, ast.Expr) and node.lineno != node.value.lineno:
                    node.lineno = node.value.lineno
                var_name = self.create_operator_lambda_var()
                self._add_operator(var_name, ast2str(node),
                                   Raw(ast2str(node), node.lineno, self.times, parallel=self.parallel))
                return ast.Name(id=var_name)

            return visit_result

        def visit_Call(self, node: ast.Call) -> Any:
            node = self._handle_special_calls(node)

            if not PaladinNativeParser._is_operator_call(node):
                return self.generic_visit(node)

            var_name = self.create_operator_lambda_var()
            # noinspection PyUnresolvedReferences,PyArgumentList,PyTypeChecker
            # Visit arguments.

            if isinstance(node.func, ast.Name) and node.func.id in {ForEach.name(), Let.name()}:
                self._extract_inner_ops = False

            arg_vars = [self._find_arg_replacement(arg) for arg in node.args if not isinstance(arg, ast.NamedExpr)]

            named_args = {arg.target.id: self._find_arg_replacement(arg.value) for arg in node.args if
                          isinstance(arg, ast.NamedExpr)}
            named_args.update({kw.arg: self._find_arg_replacement(kw.value) for kw in node.keywords})
            self._extract_inner_ops = True

            # noinspection PyArgumentList,PyUnresolvedReferences
            try:
                op = (o := PaladinNativeParser.OPERATORS[node.func.id])(self.times, *arg_vars, **named_args, parallel=self.parallel)
            except TypeError as e:
                raise SyntaxError(f'Error in operator {o.name()}')
            op.standalone = self._extract_inner_ops
            self._add_operator(var_name, ast2str(node), op)

            return ast.Name(id=var_name, lineno=node.lineno)

        def _find_arg_replacement(self, arg):
            arg_visit_result = self.visit(arg)
            if isinstance(arg_visit_result, ast.Name):
                return self.operators[arg_visit_result.id][0] if arg_visit_result.id in self.operators \
                    else self._create_raw_op_from_arg(arg_visit_result)
            elif isinstance(arg_visit_result, ast.Constant):
                return arg_visit_result.value

            elif ast2str(arg) in map(lambda o: o[1], self.operators):
                return self._create_raw_op_from_arg(self.operators[ast2str(arg_visit_result)])


            return self._create_raw_op_from_arg(arg_visit_result)

        def _handle_special_calls(self, node: ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == type.__name__:
                node.func.id = TypeOp.__name__

            if isinstance(node.func, ast.Name) and node.func.id == Old.name().lower():
                node.func.id = Old.__name__

            return node

        def visit_Slice(self, node: ast.Slice) -> Any:
            parts = []
            for part in [node.lower, node.upper, node.step]:
                if part is None:
                    parts.append(part)
                    continue
                part_visit_result = self.visit(part)

                if isinstance(part_visit_result, ast.Name) and part_visit_result.id in self.operators:
                    var_name = self.create_operator_lambda_var()
                    self._add_operator(var_name, ast2str(part),
                                       Raw(ast2str(part_visit_result), part.lineno, self.times, parallel=self.parallel))
                    parts.append(ast.Attribute(value=ast.Name(id=var_name), attr=ast2str(part)))

                else:
                    parts.append(part_visit_result)

            return ast.Slice(lower=parts[0], upper=parts[1], step=parts[2])

        def visit_Dict(self, node: ast.Dict) -> Any:
            return ast.Call(func=ast.Name(id=AttributedDict.__name__), args=[node], keywords=[], lineno=node.lineno)

        def _create_raw_op_from_arg(self, arg: ast.AST):
            r = Raw(ast2str(arg), arg.lineno, self.times, parallel=self.parallel)
            r.standalone = not self._extract_inner_ops
            return r

        def _create_const_op_from_arg(self, arg: ast.AST):
            c = Const(ast2str(arg), self.times)
            c.standalone = not self._extract_inner_ops
            return c

        def _create_type_op_from_arg(self, arg: ast.AST):
            return TypeOp(self.times, Raw(ast2str(arg), parallel=self.parallel), arg.lineno)

        def visit_Compare(self, node: ast.Compare) -> Any:
            node.left = super().visit(node.left)
            line_no = node.left.lineno
            comps = []
            for comp in node.comparators:
                comp = super().visit(comp)
                if line_no != -1 and comp.lineno != -1 and comp.lineno != line_no:
                    # In case line_no is already a real line no (not -1), and one of the comparators has a line_no,
                    # ignore all line_nos to not enforce the wrong line_no from both sides or cross-comparators.
                    line_no = -1
                elif line_no == -1 and comp.lineno != -1:
                    # If there is no line_no yet, take the comp's one.
                    line_no = comp.lineno

                comps.append(comp)

            node.comparators = comps
            node.lineno = line_no
            return node

        def visit_Name(self, node: ast.Name) -> Any:
            if PaladinNativeParser._FUNCTION_CALL_MAGIC_REPLACE_SYMBOL in node.id:
                name = node.id.replace(PaladinNativeParser._FUNCTION_CALL_MAGIC_REPLACE_SYMBOL, '')
            # elif PaladinNativeParser._COMPREHENSION_MAGIC_REPLACE_SYMBOL in node.id:
            #     name = node.id.replace(PaladinNativeParser._COMPREHENSION_MAGIC_REPLACE_SYMBOL, '')
            else:
                name = node.id

            if name != node.id:
                name = self._create_raw(name, node)

            return ast.Name(id=name, lineno=node.lineno, ctx=node.ctx if hasattr(node, 'ctx') else None)

        def _create_raw(self, name, node):
            var_name = self.create_operator_lambda_var()
            self._add_operator(var_name, name, Raw(name, node.lineno, self.times, parallel=self.parallel))
            name = var_name
            return name

        def visit_Attribute(self, node: ast.Attribute) -> Any:
            if PaladinNativeParser._COMPREHENSION_MAGIC_REPLACE_SYMBOL in node.attr:
                node.attr = node.attr.replace(PaladinNativeParser._COMPREHENSION_MAGIC_REPLACE_SYMBOL, '')
            super().visit(node.value)
            node.lineno = node.value.lineno
            return node

        # FIXME: This is a patch for the experiment's tutorial.
        def visit_BinOp(self, node):
            for operand, attr in [(node.left, 'left'), (node.right, 'right')]:
                op_visited = self.visit(cast(ast.AST, operand))
                if hasattr(op_visited, 'ctx') and op_visited.ctx == '@':
                    operator_name = self._create_raw(ast2str(op_visited), op_visited)
                    setattr(node, attr, ast.Name(id=operator_name, lineno=op_visited.lineno))
                else:
                    setattr(node, attr, op_visited)
            return node


        # def visit_comprehension(self, node: ast.comprehension) -> Any:
        #     if not (isinstance(node.iter, ast.Call) and PaladinNativeParser.OperatorLambdaReplacer._is_operator_call(
        #             node.iter)):
        #         class _Visitor(ast.NodeVisitor):
        #             def visit_Name(self, _node: ast.Name) -> Any:
        #                 _node.id = PaladinNativeParser._COMPREHENSION_MAGIC_REPLACE_SYMBOL + _node.id
        #
        #             def visit_Attribute(self, _node: ast.Attribute) -> Any:
        #                 _node.attr = PaladinNativeParser._COMPREHENSION_MAGIC_REPLACE_SYMBOL + _node.attr
        #
        #         _Visitor().visit(cast(ast.AST, node.iter))
        #
        #     node.iter = super().visit(cast(ast.AST, node.iter))
        #     node.target = super().visit(cast(ast.AST, node.target))
        #     return node

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

        def __init__(self, parser: 'PaladinNativeParser', times: Iterable[Time], root: ast.AST, parallel: bool = True):
            self.parser = parser
            self.times = times
            self.root = root
            self._lambda_var_seed = -1
            self.lambda_vars = set()
            self.operators_map = {}
            self.parallel = parallel
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
                return Raw(ast2str(node), node.lineno, self.times, parallel=self.parallel)

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

                if isinstance(o, range):
                    return str(o)

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

                    def visit_Call(self, node: ast.Call) -> Any:
                        if isinstance(node.func, ast.Name):
                            if node.func.id in {'dict_values', 'dict_keys', 'dict_items'}:
                                node.func = ast.Name(id=list.__name__)

                        return node

                return super().iterencode(
                    eval(ast2str(Tuple2StrReplacer().visit(str2ast(str(o))), _one_shot), EVAL_BUILTIN_CLOSURE))

        return PaladinNativeParser._remove_bad_json_values(json.dumps(obj, cls=_encoder))

    def parse(self, query: str, start_time: int, end_time: int, jsonify: bool = True) -> Union[str, EvalResult]:
        try:
            times = range(start_time, end_time + 1)

            # Handle function call magic symbols.
            query = PaladinNativeParser.__replace_function_call_magic(query)

            # Handle special syntax.
            query = PaladinNativeParser.__handle_special_syntax(query)

            query_ast = str2ast(query.strip().replace('\n', ' '))

            # Propagate line numbers indicated by "@" scope.
            line_no_replacer = PaladinNativeParser.LineNumberReplacer()
            line_no_replacer.visit(query_ast)

            # Replace calling to operator with lambdas.
            visitor = PaladinNativeParser.OperatorLambdaReplacer(times, parallel=self.parallel)
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

            # Add the keys in the first row.
            # noinspection PyTypeChecker
            grouped['keys'] = list(results.all_keys())

            # Remove bad JSON values.
            return self.json_dumps(grouped)

        except BaseException as e:
            traceback.print_exc()
            if jsonify:
                return json.dumps(
                    {'error': 'Syntax Error: ' + (str(e.msg) if e.msg else '') if isinstance(e,
                                                                                             SyntaxError) else 'Internal Error'})

            raise e

    def add_user_aux(self, f_content: str | bytes):
        exec(f_content, self.user_aux)

    def remove_user_aux(self):
        self.user_aux.clear()

    def _eval_operators(self, visitor):
        operator_results = {}
        for var_name, (operator, operator_original_name) in visitor.operators.items():
            if operator.standalone:
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

    @property
    def var_names(self) -> Iterable[str]:
        return self.builder.get_var_names()

    @line_no.setter
    def line_no(self, value: int) -> None:
        self._line_no = value

    @staticmethod
    def _restore_original_operator_keys(query_ast: ast.AST, visitor: OperatorLambdaReplacer, result: EvalResult) -> \
            Tuple[str, EvalResult]:
        for var_name, (operator, operator_original_name) in reversed(visitor.operators.items()):
            if {var_name} == result.all_keys() and all(
                    [isinstance(e[var_name].value, EvalResultEntry) for e in result]):
                # If the result is in the form of "lambda_var: EvalResult(...)", remove the lambda var.
                result = EvalResult([e[var_name].value if e[var_name] else e for e in result])
            else:
                result.rename_key(operator_original_name, var_name)

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

    @classmethod
    def docs(cls, supported_ops: Optional[Iterable[Type[Operator]]]) -> List[Dict]:
        if not supported_ops:
            supported_ops = Operator.all()
        time_ops = filter(lambda op: issubclass(op, TimeOperator), supported_ops)
        selectors = filter(lambda op: issubclass(op, Selector), supported_ops)
        summaries = filter(lambda op: issubclass(op, SummaryOp), supported_ops)
        aux = filter(lambda op: issubclass(op, AuxOp), supported_ops)

        return [PaladinNativeParser.create_doc('Selectors', selectors, Selector.explanation()),
                PaladinNativeParser.create_doc('Auxiliaries', aux, AuxOp.explanation()),
                PaladinNativeParser.create_doc('Summaries', summaries, SummaryOp.explanation()),
                PaladinNativeParser.create_doc('Time Operators', time_ops, TimeOperator.explanation())]

    @classmethod
    def create_doc(cls, _type: str, doced_col: Iterable, explanation: str,
                   doc_repr: Optional[Callable[[Iterable], str]] = None) -> Dict[str, str]:
        if doc_repr is None:
            doc_repr = lambda ops: '\n'.join(sorted([op.__doc__.strip() for op in ops if op.__doc__])) + '\n'

        return {'type': _type, 'doc': doc_repr(doced_col), 'exp': explanation}

    @staticmethod
    def __handle_special_syntax(query: str):
        # return PaladinNativeParser.__handle_let_args_order(query)
        return query

    @staticmethod
    def __handle_let_args_order(query: str):
        # Define the pattern to find "Let(x=1, y=2, ..., expr)"
        pattern = re.compile(r'Let\((.*)\)')

        def reorder_let(match):
            content = match.group(1)
            parts = []
            current_part = []
            stack = 0

            # Parse the content and split by top-level commas
            for char in content:
                if char == ',' and stack == 0:
                    parts.append(''.join(current_part).strip())
                    current_part = []
                else:
                    if char == '(':
                        stack += 1
                    elif char == ')':
                        stack -= 1
                    current_part.append(char)

            if current_part:
                parts.append(''.join(current_part).strip())

            # Find the expression (which doesn't contain '=' at top level)
            expr = None
            for part in parts:
                if '=' not in part.split('=', 1)[0].strip():
                    expr = part
                    break

            # Ensure we have an expression to move
            if expr is None:
                return match.group(0)

            # Collect keyword arguments
            kwargs = [part for part in parts if part != expr]

            # Reconstruct the string with expr at the beginning
            new_content = ', '.join([expr] + kwargs)
            return f'Let({new_content})'

        # Apply the reordering for each match
        corrected_s = pattern.sub(reorder_let, query)

        return corrected_s
