import functools
import itertools
import json
import operator

import pyparsing
from pyparsing import *

from archive.archive_evaluator.paladin_dsl_semantics import *


class PaladinDSLParser(object):

    def __init__(self, operators: List[Type[Operator]], archive: Archive, start_time: int, end_time: int, line_no: int):
        self._operators: List[Type[Operator]] = operators
        self.grammar: ParserElement = self.__grammar(operators)
        self.start_time = start_time
        self.end_time = end_time
        self.line_no = line_no
        self.archive = archive

    @classmethod
    def create(cls, archive: Archive, start_time: int, end_time: int, line_no: int) -> 'PaladinDSLParser':
        return PaladinDSLParser(operators=Operator.all(),
                                archive=archive, start_time=start_time, end_time=end_time, line_no=line_no)

    def __grammar(self, operators: List[Type[Operator]]) -> ParserElement:
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

        operator_queries = [Group(Keyword(k.name()) + LPAR + ZeroOrMore(query + COMMA) + query +  RPAR)
                            .set_parse_action(create_parse_action(k)) for k in Operator.all()]

        q = self._raw_query() | self._compound_query()

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

    def _compound_query(self):
        return (Suppress('{{') + ZeroOrMore(
            (SkipTo('[[') + self._raw_query())) + SkipTo(
            '}}') + Suppress('}}')).setParseAction(
            lambda q: (lambda p: p._eval_compound_query(q.asList()))
        )

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
        parsed = self.parse(query)
        if not parsed:
            return {}

        presentable = {i[0]: (i[1][0], ", ".join([f'{x[0]} -> {x[1]} [{x[2]}]' for x in i[1][1]]))
                       for i in PaladinDSLParser._group(parsed).items()}

        return json.dumps(presentable)

    @staticmethod
    def _to_ranges(iterable):
        iterable = sorted(set(iterable))
        for key, group in itertools.groupby(enumerate(iterable),
                                            lambda t: t[1] - t[0]):
            group = list(group)
            yield group[0][1], group[-1][1]

    @staticmethod
    def _group(d: Dict):
        if d == {}:
            return {}

        def create_key(key_range):
            return str((min(key_range), max(key_range)))

        keys = list(d.keys())
        key_range = []
        v = d[keys[0]]
        grouped = {}
        for k in keys:
            if d[k][0] == v[0]:
                key_range.append(k)
                continue

            grouped[create_key(key_range)] = v
            v = d[k]
            key_range = [k]

        if key_range:
            grouped[create_key(key_range)] = v
        return grouped

    @classmethod
    def docs(cls):
        return '```' '\n' + '\n'.join([op.__doc__.strip() for op in Operator.all() if op.__doc__]) + '\n' + '```'


if __name__ == '__main__':
    parser = PaladinDSLParser(
        operators=Operator.all(), archive=None, start_time=1, end_time=1229,
        line_no=92)
    parser.grammar.runTests(
        [
            'Or([[sums]]@10, [[i == 0]]@11)',
            'And([[sums]]@10, [[i == 0]]@11)',
            'Where([[sums]]@10, [[i == 0]]@11)'
        ]
    )
