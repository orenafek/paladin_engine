from dataclasses import dataclass, field
import ast
from PaladinEngine.archive.archive import Archive
from PaladinEngine.ast_common.ast_common import *

from PaladinEngine.archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import *


@dataclass
class Query(object):
    results: EvalResult

    @property
    def _passed(self) -> 'Query':
        return Query({t: (result, replacements) for (t, (result, replacements)) in self.results.items() if result})

    @property
    def _failed(self) -> 'Query':
        return Query({t: (result, replacements) for (t, (result, replacements)) in self.results.items() if not result})

    @property
    def _first(self):
        return sorted(self._passed.results.items())[0]

    @property
    def _last(self):
        return sorted(self._passed.results.items(), reverse=True)[0]

    def Also(self, query: 'Query') -> 'Query':
        return Query(
            {t1: (True, rep1 + rep2) for t1, (res1, rep1) in self.results.items() for t2, (res2, rep2) in
             query.results.items() if t1 == t2 and res1 == res2}
        )

    @classmethod
    def Not(cls, q: 'Query'):
        return q._failed

    @classmethod
    def Since(cls, q: 'Query') -> 'Query':
        return Query(
            {t: (res, rep) for t, (res, rep) in q.results.items() if t >= q._first[0]}
        )

    @classmethod
    def Before(cls, q: 'Query'):
        return Query(
            {t: (res, rep) for t, (res, rep) in q.results.items() if t < q._first[0]}
        )


Since = Query.Since
Before = Query.Before
Not = Query.Not

QUERY_DSL_WORDS = list(map(lambda f: f.__name__, [Since, Before, Not]))


@dataclass
class ArchiveEvaluator(object):
    archive: Archive

    class SymbolExtractor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.names = set()
            self.attributes = set()

        def visit_Name(self, node: ast.Name) -> Any:
            self.names.add(node.id)
            return node.id

        def visit_Attribute(self, node: ast.Attribute) -> Any:
            self.attributes.add(ast2str(node))
            self.visit(node.value)
            return self.generic_visit(node)

        def visit(self, node: ast.AST) -> 'ArchiveEvaluator.SymbolExtractor':
            super(ArchiveEvaluator.SymbolExtractor, self).visit(node)
            return self

    @dataclass
    class SymbolReplacer(ast.NodeTransformer):
        names: ExpressionMapper
        attributes: ExpressionMapper
        time: int
        replacements: List[Replacement] = field(default_factory=list)

        def __extract_value(self, expression: str, values: ExpressionMapper) -> Tuple[int, object]:
            """
                Extract a value from a mapping that is relevant to time.
            :param expression:
            :param values:
            :return:
            """
            return \
                [(t, v) for t, v in sorted(values[expression].items(), key=lambda p: p[0], reverse=True) if
                 t <= self.time][0]

        def __create_constant(self, expression: str, mapper: ExpressionMapper) -> ast.Constant:
            time, value = self.__extract_value(expression, mapper)

            self.replacements.append(Replacement(expression=expression, value=value, time=time))

            return ast.Constant(value=value, kind=str if type(value) is str else None)

        def visit_Name(self, node: ast.Name) -> Any:
            return self.__create_constant(node.id, self.names)

        def visit_Attribute(self, node: ast.Attribute) -> Any:
            return self.__create_constant(ast2str(node), self.attributes)


if __name__ == '__main__':
    pass
