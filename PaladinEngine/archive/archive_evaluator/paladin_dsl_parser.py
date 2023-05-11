import functools
import json
import operator
from typing import *

import pyparsing
from pyparsing import *

from archive.archive import Archive
from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import SCOPE_SIGN
from archive.archive_evaluator.paladin_dsl_semantics.raw import Raw
from archive.archive_evaluator.paladin_dsl_semantics.operator import Operator


class PaladinDSLParser(object):

    def __init__(self, operators: List[Type[Operator]], archive: Archive, start_time: int, end_time: int, line_no: int):
        self._operators: List[Type[Operator]] = operators
        self.grammar: ParserElement = self.__grammar()
        self.start_time = start_time
        self.end_time = end_time
        self.line_no = line_no
        self.archive = archive

    @classmethod
    def create(cls, archive: Archive, start_time: int, end_time: int, line_no: int) -> 'PaladinDSLParser':
        return PaladinDSLParser(operators=Operator.all(),
                                archive=archive, start_time=start_time, end_time=end_time, line_no=line_no)

    def __grammar(self) -> ParserElement:
        LPAR = Suppress('(')
        RPAR = Suppress(')')
        COMMA = Suppress(',')

        query = Forward()

        def create_parse_action(k):
            def parse_action(q):
                if issubclass(k, ArchiveDependent):
                    return k(self.archive, self.timer, *(q.asList()[0][1::]))
                else:
                    return k(self.timer, *(q.asList()[0][1::]))

            return parse_action

        operator_queries = [Group(Keyword(k.name()) + LPAR + ZeroOrMore(query + COMMA) + query + RPAR)
                            .set_parse_action(create_parse_action(k)) for k in Operator.all()]

        q = self._raw_query() | self._nested_query(query)

        query <<= q | functools.reduce(ParserElement.__or__, operator_queries)

        return query

    def parse(self, s: str):
        for f in self.grammar.scanString(s):
            for ff in f[0].asList():
                return ff.eval()

    def _raw_query(self):
        """
            A Raw query is either in the form [[<expression>]]@<scope (line number)> or [[<expression>]].
        :return:
        """
        return (Suppress('[[') + SkipTo(']]') + Suppress(']]') + pyparsing.Optional(Suppress(
            SCOPE_SIGN) + pyparsing_common.integer, default=None)).setParseAction(
            lambda q: Raw(self.archive, q.asList()[0], q.asList()[1], self.timer))

    def _nested_query(self, query):
        return (Suppress('{{') + CaselessKeyword('for') + Word(alphanums) + CaselessKeyword('in') + query
                + SkipTo('}}') + Suppress('}}')).setParseAction(
            lambda q: Raw(self.archive, q.asList()[1], None, self.timer, query))

    def _eval_compound_query(self, compound_query: list[str]):
        evaluated = [q(self) if callable(q) else q for q in compound_query]
        timers = [{*r.keys()} for r in evaluated if isinstance(r, dict)]
        assert all([timer == timers[0] for timer in timers])

        results = {}
        for t in timers[0]:
            query = ' '.join([str(list(r[t][0].values())[0]) if isinstance(r, dict) else r for r in evaluated])
            results[t] = (
                {query: eval(query)},
                functools.reduce(operator.add, [r[t][1] for r in evaluated if isinstance(r, dict)])
            )

        return results

    def _eval_time_slider_query(self, query: Callable, time_to_slide: int):
        return {k + time_to_slide: v for k, v in query(self).items()}

    @property
    def timer(self):
        return range(self.start_time, self.end_time + 1)

    def parse_and_summarize(self, query: str):
        # Parse the select query.
        return json.dumps(self.parse(query).group())

    @classmethod
    def docs(cls):
        return '```' '\n' + '\n'.join(
            sorted([op.__doc__.strip() for op in Operator.all() if op.__doc__])) + '\n' + '```'


if __name__ == '__main__':
    parser = PaladinDSLParser(
        operators=Operator.all(), archive=None, start_time=1, end_time=1229,
        line_no=92)
    parser.grammar.runTests(
        [
            'Or([[sums]]@10, [[i == 0]]@11)',
            'And([[sums]]@10, [[i == 0]]@11)',
            'Where([[sums]]@10, [[i == 0]]@11)',
            '{{ (e.j for e in $Line([[18]])$ ) }}'
        ]
    )
