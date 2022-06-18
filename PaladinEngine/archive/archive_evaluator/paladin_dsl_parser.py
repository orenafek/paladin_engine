import ast
import functools
import itertools
import json
from abc import ABC, abstractmethod

import pyparsing
from pyparsing import *
from archive.archive import Archive
from archive.archive_evaluator.archive_evaluator import ArchiveEvaluator
from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import *
from ast_common.ast_common import str2ast, ast2str
from archive.archive_evaluator.paladin_dsl_semantics import *


class PaladinDSLParser(object):

    def __init__(self, unilateral_keywords: List[UniLateralOperator],
                 bilateral_keywords: List[BiLateralOperator], archive: Archive, start_time: int,
                 end_time: int, line_no: int):
        self._keywords: List[Operator] = unilateral_keywords + bilateral_keywords
        self.grammar: ParserElement = PaladinDSLParser.__grammar(unilateral_keywords, bilateral_keywords)
        self.start_time = start_time
        self.end_time = end_time
        self.line_no = line_no
        self.archive = archive
        self._timer = None

    @classmethod
    def create(cls, archive: Archive, start_time: int, end_time: int, line_no: int) -> 'PaladinDSLParser':
        return PaladinDSLParser(unilateral_keywords=[op() for op in UniLateralOperator.ALL],
                                bilateral_keywords=[op() for op in BiLateralOperator.ALL],
                                archive=archive, start_time=start_time, end_time=end_time, line_no=line_no)

    @classmethod
    def __grammar(cls, unilateral_keywords: List[UniLateralOperator],
                  bilateral_keywords: List[BiLateralOperator]) -> ParserElement:
        LPAR = Suppress('(')
        RPAR = Suppress(')')
        COMMA = Suppress(',')

        query = Forward()

        unilateral_queries = [
            Group(Keyword(k.name) + LPAR + query + RPAR).setParseAction(k.create_eval) for k in unilateral_keywords
        ]
        bilateral_queries = [
            Group(Keyword(k.name) + LPAR + query + COMMA + query + RPAR).setParseAction(k.create_eval)
            for k in bilateral_keywords
        ]

        query <<= cls._raw_query() | functools.reduce(ParserElement.__or__, unilateral_queries + bilateral_queries)

        return query

    def parse(self, s: str):
        for f in self.grammar.scanString(s):
            for ff in f[0].asList():
                return ff(self)

    @classmethod
    def _raw_query(cls):
        """
            A Raw query is either in the form [[<expression>]]@<scope (line number)> or [[<expression>]].
        :return:
        """
        return (Suppress('[[') + SkipTo(']]') + Suppress(']]') + pyparsing.Optional(Suppress(
            '@') + pyparsing_common.integer, default=None)).setParseAction(
            lambda q: (lambda p: p._eval_raw_query(q.asList()[0], q.asList()[1])))

    def create_timer_for_filter(self):
        """
            Create a timer for the filter by the start and end time (not less than 0 and not more than the last archive time).
        :return:
        """
        return range(max(0, self.start_time), min(self.archive._time - 1, self.end_time + 1))

    def create_timer_after_filter(self, filter_results: Union[bool, Dict]):
        if isinstance(filter_results, bool) and not filter_results:
            return []
        if isinstance(filter_results, bool) and filter_results or filter_results is None:
            return self.create_timer_for_filter()

        # The results have filtered (not empty and not maxed).
        return filter(lambda t: filter_results[t][0], filter_results.keys())

    def _eval_raw_query(self, query: str, scope: Optional[int] = None):
        # Extract names to resolve from the archive.
        extractor = ArchiveEvaluator.SymbolExtractor()
        extractor.visit(str2ast(query))

        results = {}

        if scope is None:
            scope = self.line_no
        for t in self.timer:
            resolved_names = self._resolve_names(extractor.names, scope, t)
            resolved_attributes = self._resolve_attributes(extractor.attributes, scope, t)

            replacer = ArchiveEvaluator.SymbolReplacer(resolved_names, resolved_attributes, t)
            try:
                # TODO: Can AST object be compiled and then evaled (without turning to string)?
                result = eval(ast2str(replacer.visit(ast.parse(query))))
            except IndexError:
                result = None
            results[t] = (result, replacer.replacements)

        return results

    def _resolve_names(self, names: Set[str], line_no: int, time: int) -> ExpressionMapper:
        """
            Resolves the values of the objects in names from the archive.
        :param names: A set of names to resolve.
        :param line_no: The line no in which to look for the scope of the object.
        :param time: The time in which the object's value should be resolved.
        :return:
        """
        return {name: self.archive.find_by_line_no(name, line_no, time)[name] for name in names}

    def _resolve_attributes(self, attributes: Set[str], line_no: int, time: int) -> ExpressionMapper:
        return {attr: self.archive.find_by_line_no(attr, line_no, time)[attr] for attr in attributes}

    @property
    def timer(self):
        return self._timer

    @timer.setter
    def timer(self, value):
        self._timer = value

    def parse_and_summarize(self, select_query: str, where_query: Optional[str] = ''):
        # TODO: Remove where query.
        # Set timer for filtering by where.
        self.timer = self.create_timer_for_filter()

        # Parse the where query.
        parsed_and_filtered_by_where = self.parse(where_query)
        if isinstance(parsed_and_filtered_by_where, bool) and not parsed_and_filtered_by_where:
            return {}

        # Create timer for the select query by the filtering.
        self.timer = self.create_timer_after_filter(parsed_and_filtered_by_where)

        # Parse the select query.
        parsed_select = self.parse(select_query)
        if not parsed_select:
            return {}

        presentable_and_filtered = {i[0]: (str(i[1][0]), ", ".join([f'{x[0]} -> {x[1]} [{x[2]}]' for x in i[1][1]])) for
                                    i in
                                    parsed_select.items() if i[1][0] != True}

        # TODO: Change format to fit into tabular vue component.
        return {json.dumps(i[1][0]): i[0] for i in sorted(
            {val: tuple(PaladinDSLParser._to_ranges(
                [k for k in presentable_and_filtered if presentable_and_filtered[k] == val])) for val
                in set(presentable_and_filtered.values())}.items())}

    @staticmethod
    def _to_ranges(iterable):
        iterable = sorted(set(iterable))
        for key, group in itertools.groupby(enumerate(iterable),
                                            lambda t: t[1] - t[0]):
            group = list(group)
            yield group[0][1], group[-1][1]


if __name__ == '__main__':
    parser = PaladinDSLParser(
        unilateral_keywords=[Globally(), Next(), Finally()],
        bilateral_keywords=[Until()], archive=None, start_time=1, end_time=1229, line_no=92)
    parser.grammar.runTests(
        ['[[e < self.V - 1]]', 'G([[e == 4]])', 'U([[e < self.V - 1]], [[e == 4]])', 'U(G([[e < self.V - 1]]), [[9]])'])
