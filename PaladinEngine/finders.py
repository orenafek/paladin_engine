from conf.engine_conf import *


class DecoratorFinder(ast.NodeVisitor):
    """
    TODO: Doc.
    """

    def __init__(self) -> None:
        """
            Constructor.
        """
        # Call the super's constructor.
        super().__init__()

    def visit_FunctionDef(self, node):
        print('Visited: \n{dl}\ndef {n}({a})'.format(
            dl=self.__decorator_list_to_str(node),
            a=', '.join(self.__args_to_str(node)),
            n=node.name,
        ))
        self.generic_visit(node)

    def __args_to_str(self, node):
        args = []
        for a in node.args.args:
            args.append(a.arg)

        return ', '.join(args)

    def __decorator_list_to_str(self, node):
        decorators = []

        for d in node.decorator_list:
            decorators.append('@{name}({args})'.format(name=d.func.value.id,
                                                       args=[a.s for a in d.args]))
        return '\n'.join(decorators)


class PaladinInlineDefinitionFinder(ast.NodeVisitor):
    """
    TODO: doc.
    """

    def __init__(self) -> None:
        """
            Constructor.
        """
        # Call the super's constructor.
        super().__init__()

        # Initialize a dict of loops and their inline definitions.
        self.loop_map = {}

        # Initialize the "has visited flag".
        self.visited = False

    def visit(self, node):
        # Mark the node as visited.
        self.visited = True

        # Visit.
        super(PaladinInlineDefinitionFinder, self).visit(node)

    def visit_For(self, node) -> None:
        """
            A visitor for For Loops.
        :param node: (ast.AST) An AST node.
        :return: None.
        """
        self.__add_node_to_map(node)
        self.generic_visit(node)

    def visit_While(self, node) -> None:
        """
            A visitor for While Loops.
        :param node: (ast.AST) An AST node.
        :return: None.
        """
        self.__add_node_to_map(node)
        self.generic_visit(node)

    def __add_node_to_map(self, node) -> None:
        """
            Add the node the inner map.
        :param node: (ast.AST) An AST node.
        :return:
        """
        self.loop_map[node] = None

    def visit_Str(self, node):
        """
            TODO: doc.
        :param node:
        :return:
        """

        # If not an inline definition, leave.
        if not PaladinInlineDefinitionFinder.__is_inline_def(node):
            return

        # Find the matching loop.
        matching_loop = [loop for loop in self.loop_map.keys() if
                         PaladinInlineDefinitionFinder.__is_first_or_only_stmt_of_body(node, loop)][0]

        # Fill in the map.
        self.loop_map[matching_loop] = node

    def print_all(self):
        """
            TODO: doc.
        :return:
        """
        print([PaladinInlineDefinitionFinder.__expr_node_to_str(node) for node in self.loop_map.values()])

    @staticmethod
    def __is_first_or_only_stmt_of_body(node, loop):
        """
            Tests if a node is the first statement of a loop.

        :param node: (ast.AST) An AST node.
        :param loop: (ast.stmt) A Loop.
        :return: True <==> the node is the only or first statement of the body.
        """
        return (type(loop.body) is list and loop.body[0].value is node) or loop.body.value is node

    @staticmethod
    def __is_inline_def(node):
        """
            Identifies an inline definition of an Expr node.
        :param node: (ast.Expr) An expr node.
        :return: true <==> the Expr has a header of a paladin inline definition.
        """
        if not isinstance(node, ast.Str):
            raise NotImplementedError()

        # Strip.
        striped_node = PaladinInlineDefinitionFinder.__expr_node_to_str(node).strip()

        return striped_node.startswith(PALADIN_INLINE_DEFINITION_HEADER) and \
               striped_node.endswith(PALADIN_INLINE_DEFINITION_FOOTER)

    @staticmethod
    def __expr_node_to_str(node) -> str:
        """
            Extracts the node to a str.
        :param node: an Expr node.
        :return: (str) The string represents the node.
        """
        if not isinstance(node, ast.Str):
            raise NotImplementedError()

        return node.s

    @staticmethod
    def __strip_header_and_footer(node_str) -> str:
        """
            TODO: doc.
        :param node:
        :return:
        """
        return node_str.lstrip(PALADIN_INLINE_DEFINITION_HEADER).rstrip(PALADIN_INLINE_DEFINITION_FOOTER)

    def inline_loops(self):
        """
            Returns the loops that the PaLaDiN definitions validate.
        :return:
        """

        if not self.visited:
            raise NotVisitedException()

        return {pair[0]: pair[1] for pair in self.loop_map.items() if pair[1] is not None}


class DanglingPaLaDiNDefinition(Exception):
    """
        An exception for a dangling PaLaDin assertion.
    """
    pass


class DanglingPaLaDiNInlineDefinition(DanglingPaLaDiNDefinition):
    """
        An exception for a dangling PaLaDiN's inline assertion.
    """
    pass


class NotVisitedException(Exception):
    """
        An exception for when trying to operate on objects that should be visited first.
    """
    pass
