from PaladinEngine.archive.archive import Archive
from PaladinEngine.archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import *
from PaladinEngine.ast_common.ast_common import *


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
            try:
                return self.__create_constant(node.id, self.names)

            except KeyError or IndexError:
                return node

        # def visit_Attribute(self, node: ast.Attribute) -> Any:
        #     try:
        #         return self.__create_constant(ast2str(node), self.attributes)
        #
        #     except KeyError or IndexError:
        #         return node
