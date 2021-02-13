from abc import ABC, abstractmethod
from typing import Union

from PaladinEngine.conf.engine_conf import *
from PaladinEngine.api.api import PaladinPostCondition
from PaladinEngine.stubs import StubArgumentType


class StubEntry(object):
    """
        A triple of an element to stub, its container and the attr name in which it is held.
    """

    def __init__(self, node, attr_name, container, extra=None):
        self._node = node
        self._attr_name = attr_name
        self._container = container
        self._extra = extra

    @property
    def node(self):
        return self._node

    @property
    def attr_name(self):
        return self._attr_name

    @property
    def container(self):
        return self._container

    @property
    def extra(self):
        return self._extra

    def __str__(self):
        return f'node = {self.node}\n' \
               f'attr_name = {self.attr_name}\n' \
               f'container = {self.container}\n' \
               f'extra = {self.extra}\n'


class SliceStubEntry(StubEntry):

    def __init__(self, node, attr_name, container, indices):
        super().__init__(node, attr_name, container)
        self._indices = indices

    @property
    def indices(self):
        return self._indices


class GenericFinder(ABC, ast.NodeVisitor):
    """
        A generic finder for any ast.AST object.
    """

    def __init__(self) -> None:
        """
            Constructor.
        """
        # Call the super's constructor.
        super().__init__()

        # Initialize the found entries.
        self.__entries = []

        # A list for keeping track of the nodes being visited by this visitor.
        self.__visited_notes = []

    def visit(self, node) -> None:
        """
            General visit.
        :param node: (ast.AST) An AST node.
        :return: None.
        """
        # Check if visited before.
        if node in self.__visited_notes:
            return

        # Add to visits list.
        self.__visited_notes.append(node)

        # Search in direct children nodes.
        for attr_name, child_node in GenericFinder.__iter_child_nodes(node):
            # Check if this node should be visited.
            if self._should_visit(child_node):
                # Visit and keep the extra information created by the visit in this node.
                extra = super().visit(child_node)
                # If there is an extra information, this child node should be stored for later reference.
                if extra:
                    self._store_entry(StubEntry(child_node, attr_name, node, extra))
                else:
                    # This child_entry is not interesting for storing, but continue searching in its descendants.
                    self.generic_visit(child_node)

        # Visit by super's visitor.
        super().generic_visit(node)

    def _should_visit(self, child_node: ast.AST) -> bool:
        """
            Should the child_node be visited or not.
        :param child_node: An ast.AST node.
        :return: bool
        """
        # Get the types that this visitor is searching for.
        types_to_find = self.types_to_find()

        # If the types to find is a list of types.
        if type(types_to_find) is list:
            # Search in the list.
            return type(child_node) in types_to_find

        # The type is singular, check if the child_node's type matches it.
        return types_to_find is type(child_node)

    @staticmethod
    def __iter_child_nodes(node):
        """
        Yield all direct child nodes of *node*, that is, all fields that are nodes
        and all items of fields that are lists of nodes.
        """
        for name, field in ast.iter_fields(node):
            if isinstance(field, ast.AST):
                yield name, field
            elif isinstance(field, list):
                for item in field:
                    if isinstance(item, ast.AST):
                        yield name, item

    def find(self) -> list:
        """
            Returns the results of the find.
        :return:
        """
        if not self.__visited_notes:
            raise NotVisitedException()

        return self.__entries

    @abstractmethod
    def types_to_find(self) -> Union:
        """
        The types that this finder should find.
        Must be overridden by successors.
        :return: A type or a list of types.
        """
        raise NotImplementedError()

    def _store_entry(self, entry: StubEntry) -> None:
        """
        Store a StubEntry.
        :param: entry: A StubEntry.
        :return: None
        """
        self.__entries.append(entry)

    def _extract_extra(self, node: ast.AST):
        """
            Extract the important value from a node.
        :param node: An ast.AST node.
        :return:
        """
        return node

    def _generic_visit_with_extras(self, node, extra) -> list:
        """
            Generic-Visit a node and return the extras of this node and the results of the generic visit.
        :param node: An ast.AST node.
        :param extra: The extra from the visit in node.
        :return: list of extras.
        """
        rest_of_extras = self.generic_visit(node)
        if rest_of_extras is None:
            return extra
        elif rest_of_extras is list:
            return [extra] + rest_of_extras
        else:
            return [extra, rest_of_extras]


class DecoratorFinder(GenericFinder):
    """
    A finder for function decorators.
    """

    def __init__(self) -> None:
        """
            Constructor.
        """
        # Call the super's constructor.
        super().__init__()

        # Create a list for all decorators
        self.__decorators = {}

    def visit_FunctionDef(self, node):
        # Collect decorators.
        decorators = []
        for decorator in node.decorator_list:
            if self._decorator_predicate(node, decorator):
                decorators.append(DecoratorFinder.Decorator(node, decorator))
        return self._generic_visit_with_extras(node, decorators)

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def _decorator_predicate(self, func: ast.FunctionDef, decorator: ast.expr):
        """
            A predicate to filter found decorators.
        :param decorator:  A decorator object.
        :return: True if the decorator should be added.
        """
        return True

    def types_to_find(self):
        return ast.FunctionDef

    def _extract_extra(self, node: ast.AST):
        return self.__decorators[node]

    class Decorator(object):
        def __init__(self, func: ast.FunctionDef, decorator: ast.expr):
            # Check decorator type.
            if isinstance(decorator, ast.Call):
                # The decorator name.
                dec_name = decorator.func

                # The decorator has params.
                params = [arg.s for arg in decorator.args]

            elif isinstance(decorator, ast.Name):
                dec_name = decorator
                # The decorator has no params.
                params = []

            else:
                # The decorator is of an unfamiliar type.
                raise AssertionError('An unfamiliar decorator.')

            # Store containing function.
            self.func = func

            # Store decorator name.
            self._name = dec_name.id

            # Store decorator params.
            self._params = params

        @property
        def name(self):
            return self._name

        @property
        def params(self):
            return self._params


class PaladinForLoopFinder(GenericFinder):
    """
    A finder for While & For loops invariants.
    """

    def __init__(self) -> None:
        """
            Constructor.
        """
        # Call the super's constructor.
        super().__init__()

        # Initialize a dict of loops and their inline definitions.
        self.for_loops = []

    def visit_For(self, node) -> None:
        """
            A visitor for For Loops.
        :param node: (ast.AST) An AST node.
        :return: None.
        """
        self.for_loops.append(node)
        return True

    def _extract_extra(self, node: ast.AST):
        if node in self.for_loops:
            return self.for_loops[node]

        return None

    def types_to_find(self) -> Union:
        return [ast.For]


class PaladinForLoopInvariantsFinder(GenericFinder):
    """
    A finder for While & For loops invariants.
    """

    def __init__(self) -> None:
        """
            Constructor.
        """
        # Call the super's constructor.
        super().__init__()

        # Initialize the loop map.
        self.loop_map = {}

    def visit_For(self, node) -> None:
        """
            A visitor for For Loops.
        :param node: (ast.AST) An AST node.
        :return: None.
        """
        return self.__visit_loop(node)

    def visit_While(self, node):
        """
            A visitor for While Loops.
        :param node: (ast.AST) An AST node.
        :return: None.
        """
        return self.__visit_loop(node)

    def __visit_loop(self, node):
        self.loop_map[node] = []
        for inner_node in node.body:
            if type(inner_node) is ast.Expr:
                self.visit_Expr(inner_node)

        return self.loop_map[node]

    def visit_Expr(self, node):
        """
            TODO: doc.
        :param node:
        :return:
        """

        # If not a loop invariant, leave.
        if not PaladinForLoopInvariantsFinder.__is_loop_invariant(node):
            return

        # If no loops have been visited before, leave.
        if self.loop_map == {}:
            return

        # Find the matching loop.
        matching_loop = [loop for loop in self.loop_map.keys() if
                         PaladinForLoopInvariantsFinder.__is_first_or_only_stmt_of_body(node, loop)][0]

        # Fill in the map.
        self.loop_map[matching_loop] = node

        return matching_loop

    @staticmethod
    def __is_first_or_only_stmt_of_body(node, loop):
        """
            Tests if a node is the first statement of a loop.

        :param node: (ast.AST) An AST node.
        :param loop: (ast.stmt) A Loop.
        :return: True <==> the node is the only or first statement of the body.
        """
        return (type(loop.body) is list and loop.body[0] is node) or loop.body is node

    @staticmethod
    def __is_loop_invariant(node):
        """
            Identifies a loop invariant.
        :param node: (ast.Expr) An expr node.
        :return: true <==> the Expr has a header of a paladin inline definition.
        """
        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Constant) \
                or not isinstance(node.value.value, str):
            return False

        # Strip.
        striped_node = PaladinForLoopInvariantsFinder.__expr_node_to_str(node).strip()

        return striped_node.startswith(PALADIN_INLINE_DEFINITION_HEADER) \
               and striped_node.endswith(PALADIN_INLINE_DEFINITION_FOOTER)

    @staticmethod
    def __expr_node_to_str(node) -> str:
        """
            Extract a string from an ast.Str node.
        :param node: an Expr node.
        :return: (str) The string represents the node.
        """
        return node.value.value

    def types_to_find(self) -> Union:
        return [ast.For, ast.While]


class AssignmentFinder(GenericFinder):
    """
        Finds all assignment statements in the node.
    """

    def __init__(self) -> None:
        super().__init__()

    def types_to_find(self):
        return ast.Assign

    def _add_to_assign(self, name, attr=None):
        if attr is not None:
            target_string = name + "." + str(attr)
        else:
            target_string = name

        return [(target_string, StubArgumentType.NAME), (target_string, StubArgumentType.PLAIN)]

    def visit_Assign(self, node):
        extras = []

        for target in node.targets:
            if type(target) is ast.Tuple:
                extras.extend(self.visit_Tuple(target))
            else:
                extras.append(super(GenericFinder, self).visit(target))

        # return extras
        return self._generic_visit_with_extras(node, extras)

    def visit_Name(self, node):
        return self._add_to_assign(node.id)

    def visit_Attribute(self, node):
        # Extract Name.
        name = node.value.id
        return self._add_to_assign(name, node.attr)

    def visit_Subscript(self, node):
        # Visit value (the object being subscripted) to extract extra.
        value_extra = super(GenericFinder, self).visit(node.value)

        class SliceFinder(ast.NodeVisitor):

            def visit_Tuple(self, node):
                return [self.visit(elem) for elem in node.elts]

            def visit_Name(self, node):
                return node.id, StubArgumentType.NAME

            def visit_Attribute(self, node):
                return node.attr, StubArgumentType.NAME

            def visit_Slice(self, node):
                return self.visit(node.lower), self.visit(node.upper), self.visit(node.step)

        # Take extra for the slice.
        slice_extra = SliceFinder().visit(node.slice)

        # Create a subscript tuple.
        return [value_extra, slice_extra]

    def visit_Tuple(self, node):
        extras = []
        for tuple_target in node.elts:
            extras.append(super(GenericFinder, self).visit(tuple_target))

        return extras


class PaladinPostConditionFinder(DecoratorFinder):
    """
        Finds post conditions of functions in the form:
        @PaladinPostCondition(...)
        def <func_name>(...):
            ...
    """

    def _decorator_predicate(self, func: ast.FunctionDef, decorator: ast.expr):
        return DecoratorFinder.Decorator(func, decorator).name == PaladinPostCondition.__name__


class DanglingPaLaDiNDefinition(Exception):
    """
        An exception for a dangling PaLaDin assertion.
    """
    pass


class NotVisitedException(Exception):
    """
        An exception for when trying to operate on objects that should be visited first.
    """
    pass
