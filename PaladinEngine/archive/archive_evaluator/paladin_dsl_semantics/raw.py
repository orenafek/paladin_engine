import ast
import traceback
from typing import Optional, Iterable, Dict, Set, Collection, Union, List, Any, Callable

from archive.archive_evaluator.archive_evaluator import ArchiveEvaluator
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import EvalResult, EVAL_BUILTIN_CLOSURE, \
    EvalResultEntry, EvalResultPair, ExpressionMapper, LineNo
from archive.archive_evaluator.operator_eval_results import OperatorEvalData
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

    def eval(self, eval_data):
        # Extract names to resolve from the builder.
        extractor = ArchiveEvaluator.SymbolExtractor()
        extractor.visit(str2ast(self.query))

        # Split query into sub queries.
        queries = split_tuple(self.query)

        # Check for a comprehension.
        if any([isinstance(str2ast(self.query).value, t) for t in {ast.ListComp, ast.SetComp, ast.DictComp}]):
            return self._evaluate_comprehension(queries, eval_data.query_locals)

        return self._evaluate_raw_by_time(extractor, queries, eval_data)

    def _evaluate_raw_by_time(self, extractor, queries, eval_data: OperatorEvalData):

        results = []
        for t in self.times:
            resolved_names = self._resolve_names(extractor.names, self.line_no, t, eval_data)
            try:
                # TODO: Can AST object be compiled and then evaled (without turning to string)?
                result = eval(self.query, {**EVAL_BUILTIN_CLOSURE, **resolved_names})
            except (IndexError, KeyError, NameError, AttributeError, TypeError):
                result = [None] * len(queries) if len(queries) > 1 else None
            results.append(self._create_evald_result(queries, result, t))
        return EvalResult(results)

    def _evaluate_comprehension(self, queries, query_locals):
        try:
            evald = eval(self.query, {**EVAL_BUILTIN_CLOSURE, **{n: query_locals[n] for n in query_locals}})
        except (IndexError, KeyError, NameError, AttributeError, TypeError):
            evald = [None] * len(self.times)
        results = [self._create_evald_result(queries, evald[t], t) for t in self.times]
        return EvalResult(results)

    def _create_evald_result(self, queries: Union[List[str], str], result: Any, t: Time):
        return EvalResultEntry(t,
                               [EvalResultPair(self.create_key(q), r) for q, r in zip(queries, result)]
                               if len(queries) > 1
                               else [EvalResultPair(self.create_key(self.query), result)],
                               [])

    def create_key(self, query: str):
        return f'{query}{SCOPE_SIGN}{self.line_no}' if self.line_no is not None and self.line_no != -1 else f'{query}'

    @staticmethod
    def _resolve_names(names: Set[str], line_no: int, time: int, eval_data: OperatorEvalData) -> ExpressionMapper:
        """
            Resolves the values of the objects in names from the builder.
        :param names: A set of names to resolve.
        :param line_no: The line no in which to look for the scope of the object.
        :param time: The time in which the object's value should be resolved.
        :return:
        """
        resolved = {name: eval_data.builder.build(name, time, line_no=line_no) for name in names}
        # Delete empty results (for names that couldn't be found).
        resolved = {name: resolved[name] for name in resolved if resolved[name] is not None}

        if eval_data.query_locals:
            for name in eval_data.query_locals:
                if eval_data.query_locals[name]:
                    vals_for_name = sorted([e for e in eval_data.query_locals[name] if e.time <= time], reverse=True,
                                           key=lambda e: e.time)
                    if vals_for_name:
                        val = vals_for_name[0]
                        if Let.LET_BOUNDED_KEY in val:
                            res = val[Let.LET_BOUNDED_KEY].value
                        else:
                            res = val
                    else:
                        res = EvalResultEntry.empty(time)
                    resolved.update({name: res})

        if eval_data.user_aux:
            resolved.update({k: v for k, v in eval_data.user_aux.items() if v is not None and k in names})

        if eval_data.bounded:
            resolved.update(eval_data.bounded)
        return resolved

    def _get_args(self) -> Collection['Operator']:
        return []
