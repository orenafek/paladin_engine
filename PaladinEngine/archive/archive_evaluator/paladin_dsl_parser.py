import ast
import functools
from abc import ABC, abstractmethod

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
        return Suppress('[[') + SkipTo(']]').setParseAction(
            lambda q: (lambda p: p._eval_raw_query(q.asList()[0]))) + Suppress(']]')

    def _eval_raw_query(self, query: str):
        # Extract names to resolve from the archive.
        extractor = ArchiveEvaluator.SymbolExtractor()
        extractor.visit(str2ast(query))

        results = {}

        resolved_names = self._resolve_names(extractor.names, self.line_no)
        resolved_attributes = self._resolve_attributes(extractor.attributes, self.line_no)

        for t in range(self.start_time, self.end_time + 1):
            replacer = ArchiveEvaluator.SymbolReplacer(resolved_names, resolved_attributes, t)

            result = eval(ast2str(replacer.visit(ast.parse(query))))
            results[t] = (result, replacer.replacements)

        return results

    def _resolve_names(self, names: Set[str], line_no: int) -> ExpressionMapper:
        """
            Resolves the values of the objects in names from the archive.
        :param names: A set of names to resolve.
        :param line_no: The line no in which to look for the scope of the object.
        :param time: The time in which the object's value should be resolved.
        :return:
        """
        return {name: self.archive.find_by_line_no(name, line_no)[name] for name in names}

    def _resolve_attributes(self, attributes: Set[str], line_no: int) -> ExpressionMapper:
        return {attr: self.archive.find_by_line_no(attr, line_no)[attr] for attr in attributes}


if __name__ == '__main__':
    parser = PaladinDSLParser(
        unilateral_keywords=[Globally(), Next(), Finally()],
        bilateral_keywords=[Until()], archive=None, start_time=1, end_time=1229, line_no=92)
    parser.grammar.runTests(
        ['[[e < self.V - 1]]', 'G([[e == 4]])', 'U([[e < self.V - 1]], [[e == 4]])', 'U(G([[e < self.V - 1]]), [[9]])'])
