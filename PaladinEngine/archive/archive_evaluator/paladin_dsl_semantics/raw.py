import ast
import traceback
from typing import Optional, Iterable, Dict, Set, Collection, Union, List, Any, Callable

from archive.archive_evaluator.archive_evaluator import ArchiveEvaluator
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EVAL_BUILTIN_CLOSURE, \
    EvalResultEntry, EvalResultPair, ExpressionMapper, LineNo, AttributedDict
from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import SCOPE_SIGN
from archive.archive_evaluator.paladin_dsl_semantics.let import Let
from archive.archive_evaluator.paladin_dsl_semantics.operator import Operator
from archive.archive_evaluator.paladin_dsl_semantics.semantic_utils import Time
from archive.object_builder.object_builder import ObjectBuilder
from ast_common.ast_common import str2ast, split_tuple


class Raw(Operator):
    """
    Raw(expr): The basic operator to retrieve data and evaluate expressions with data from the log.
               Can be used in an implied form, i.e., Raw(x) <==> x.

    """

    def __init__(self, query: str, line_no: Optional[LineNo] = -1, times: Optional[Iterable[Time]] = None):
        Operator.__init__(self, times)
        self.query = query
        self.line_no = line_no

    def eval(self, builder: ObjectBuilder, query_locals: Optional[Dict[str, EvalResult]] = None,
             user_aux: Optional[Dict[str, Callable]] = None):
        # Extract names to resolve from the builder.
        extractor = ArchiveEvaluator.SymbolExtractor()
        extractor.visit(str2ast(self.query))

        # Split query into sub queries.
        queries = split_tuple(self.query)

        # Check for a comprehension.
        if any([isinstance(str2ast(self.query).value, t) for t in {ast.ListComp, ast.SetComp, ast.DictComp}]):
            pass

        return self._evaluate_raw_by_time(builder, extractor, queries, query_locals, user_aux)

    def _evaluate_raw_by_time(self, builder, extractor, queries, query_locals, user_aux: Dict[str, Callable]):

        results = []
        for t in self.times:
            resolved_names = self._resolve_names(builder, extractor.names, self.line_no, t, query_locals, user_aux)
            try:
                # TODO: Can AST object be compiled and then evaled (without turning to string)?
                result = eval(self.query, {**resolved_names, **EVAL_BUILTIN_CLOSURE})
            except (IndexError, KeyError, NameError, AttributeError, TypeError):
                result = [None] * len(queries) if len(queries) > 1 else None
            results.append(self._create_evald_result(queries, result, t))
        return EvalResult(results)

    def _evaluate_comprehension(self, queries, query_locals):
        try:
            evald = eval(self.query, {**EVAL_BUILTIN_CLOSURE, **Raw.query_locals_for_compr(query_locals)})
        except (IndexError, KeyError, NameError, AttributeError, TypeError):
            evald = [None] * len(self.times)
        results = [self._create_evald_result(queries, evald[t], t) for t in self.times]
        return EvalResult(results)

    @staticmethod
    def query_locals_for_compr(query_locals: Dict[str, EvalResult]) -> Dict[str, Any]:
        return {qk: [AttributedDict(e.items_no_scope_signs) for e in qv] for qk, qv in query_locals.items()}

    def _create_evald_result(self, queries: Union[List[str], str], result: Any, t: Time):
        return EvalResultEntry(t,
                               [EvalResultPair(self.create_key(q), r) for q, r in zip(queries, result)]
                               if len(queries) > 1
                               else [EvalResultPair(self.create_key(self.query), result)],
                               [])

    def create_key(self, query: str):
        return f'{query}{SCOPE_SIGN}{self.line_no}' if self.line_no is not None and self.line_no != -1 else f'{query}'

    @staticmethod
    def _resolve_names(builder: ObjectBuilder, names: Set[str], line_no: int, time: int,
                       query_locals: Dict[str, EvalResult], user_aux: Dict[str, Callable]) -> ExpressionMapper:
        """
            Resolves the values of the objects in names from the builder.
        :param names: A set of names to resolve.
        :param line_no: The line no in which to look for the scope of the object.
        :param time: The time in which the object's value should be resolved.
        :return:
        """
        resolved = {name: builder.build(name, time, line_no=line_no) for name in names}
        # Delete empty results (for names that couldn't be found).
        resolved = {name: resolved[name] for name in resolved if resolved[name] is not None}

        if query_locals:
            for name in query_locals:
                if query_locals[name]:
                    vals_for_name = sorted([e for e in query_locals[name] if e.time <= time], reverse=True,
                                           key=lambda e: e.time)
                    if vals_for_name:
                        val = vals_for_name[0]
                        if Let.LET_BOUNDED_KEY in val:
                            res = val[Let.LET_BOUNDED_KEY].value
                        elif isinstance(val, EvalResultEntry):
                            if len(val.keys) == 0:
                                res = EvalResultEntry.empty(time)
                            elif len(val.keys) > 1:
                                # res = val.items_no_scope_signs
                                res = val
                            else:
                                res = val.values[0]
                        else:
                            res = val
                    else:
                        res = EvalResultEntry.empty(time)
                    resolved.update({name: res})

        if user_aux:
            resolved.update({k: v for k, v in user_aux.items() if v is not None})

        return resolved

    def _get_args(self) -> Collection['Operator']:
        return []
