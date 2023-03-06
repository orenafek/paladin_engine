import ast
from _ast import AST
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union, Optional, List, Type, Any, NamedTuple, Tuple, Iterable

from api.api import PaladinPostCondition
from ast_common.ast_common import ast2str
from conf.engine_conf import *
from stubs.stubs import StubArgumentType, all_stubs, SubscriptVisitResult


@dataclass
class StubEntry(object):
    """
        A triple of an element to stub, its container and the attr name in which it is held.
    """
    node: ast.AST
    attr_name: str
    line_no: int
    container: ast.AST
    extra: object = None

    def __str__(self):
        return f'node = {self.node}\n' \
               f'attr_name = {self.attr_name}\n' \
               f'container = {self.container}\n' \
               f'extra = {self.extra}\n'


class SliceStubEntry(StubEntry):
    def __init__(self, node, attr_name, line_no, container, indices):
        super().__init__(node, attr_name, line_no, container)
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
        self._entries: List[StubEntry] = []

        # A list for keeping track of the nodes being visited by this visitor.
        self.__visited_notes = []

        self._containers = []

    def _should_store_entry(self, extra: Union[None, object]) -> bool:
        """
            Should store the entry after a visit.
        :param extra: An extra information object that has been created in a visit.
        :return: True if the entry should be stored and False otherwise.
        """
        return extra is not None

    def visit(self, node) -> None:
        try:
            """
                General visit.
            :param node: (ast.AST) An AST node.
            :return: None.
            """
            # Check if visited before.
            if node in self.__visited_notes:
                return

            if self._should_filter(node):
                return

            # Add to visits list.
            self.__visited_notes.append(node)

            # Store container of container.
            self._containers.insert(0, node)

            # Search in direct children nodes.
            for attr_name, child_node in GenericFinder._iter_child_nodes(node):

                # Check if this node should be visited.
                if self._should_visit(node, child_node):
                    # Visit and keep the extra information created by the visit in this node.
                    extra = super().visit(child_node)
                    # If there is extra information, this child node should be stored for later reference.
                    if self._should_store_entry(extra):
                        self._store_entry(StubEntry(child_node, attr_name, child_node.lineno, node, extra))
                    else:
                        # This child_entry is not interesting for storing, but continue searching in its descendants.
                        self.generic_visit(child_node)

            # Visit by super's visitor.
            super().generic_visit(node)

            # Pop from the containers stack.
            self._containers.pop(0)

        except BaseException as e:
            print(e)

    def _should_visit(self, node: ast.AST, child_node: ast.AST) -> bool:
        """
            Should the child_node be visited or not.

        :param node: An ast.AST node.
        :param child_node: One of node's direct node children.
        :return: bool
        """
        # Get the types that this visitor is searching for.
        types_to_find = self.types_to_find()

        return any([isinstance(child_node, t) for t in types_to_find]) \
            if isinstance(types_to_find, Iterable) else isinstance(child_node, types_to_find)

    @staticmethod
    def _iter_child_nodes(node) -> Tuple[str, ast.AST]:
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

    @staticmethod
    def get_node_attr_name(node: ast.AST, child_node: ast.AST) -> str:
        for name, field in ast.iter_fields(node):
            if isinstance(field, ast.AST) and field is child_node:
                return name
            elif isinstance(field, list):
                for item in field:
                    if isinstance(item, ast.AST) and item is child_node:
                        return name

    def find(self) -> List[StubEntry]:
        """
            Returns the results of the find.
        :return:
        """
        if not self.__visited_notes:
            raise NotVisitedException()

        return self._entries

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
        self._entries.append(entry)

    def _get_visited_node_extra(self, node) -> Optional[object]:
        """
            Get an extra object of a visited node, if such exist.
        @param node: A (most likely previously visited) node.
        @return: The extra object if one could have been found.
        """
        for e in self._entries:
            if e.node == node:
                return e.extra

        return None

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

    def _should_filter(self, node: ast.AST) -> bool:
        is_stub_call = isinstance(node, ast.Call) and ast2str(node.func).startswith('__')
        is_stub_assign = isinstance(node, ast.Assign) and ast2str(node).startswith('____')
        is___str___call = isinstance(node, ast.FunctionDef) and node.name == '__str__'
        return is_stub_call or is_stub_assign or is___str___call

    def _safe_visit(self, node):
        if not node:
            return None

        return self.visit(node)


class ContainerFinder(GenericFinder):

    def __init__(self, child_node: ast.AST):
        super().__init__()
        self.target_child_node = child_node
        self.container = None
        self.attr_name = None

    def visit(self, node) -> Optional[Tuple[ast.AST, str]]:
        for attr_name, child_node in GenericFinder._iter_child_nodes(node):
            if id(child_node) == id(self.target_child_node):
                self.container = node
                self.attr_name = attr_name

        return self.generic_visit(node)

    def types_to_find(self) -> Union:
        return ast.AST


class FinderByString(GenericFinder):
    """
        A Finder for a node by a string.
    """

    TYPES_TO_EXCLUDE = [ast.Expr, ast.Expression, ast.FormattedValue,
                        ast.JoinedStr]

    def __init__(self, s):
        self.should_visit_counter = 0
        self.s = s
        super().__init__()

    def types_to_find(self) -> Union:
        return ast.AST

    def _should_visit(self, node: ast.AST, child_node: ast.AST) -> bool:
        # If the string to find is included in the node.
        string_included = self.s in ast2str(child_node)

        # If the node has a field that can be extended (is a list).
        can_node_be_extended = [f for f in node._fields if type(node.__getattribute__(f)) == list] != []

        # If the node should be excluded because of its type.
        should_node_be_excluded_by_type = node in FinderByString.TYPES_TO_EXCLUDE

        return string_included and can_node_be_extended and not should_node_be_excluded_by_type

    def _should_store_entry(self, extra: Union[None, object]) -> bool:
        return True

    @staticmethod
    def find_first_occurrence(s: str, node: ast.AST) -> Optional[ast.AST]:
        finder = FinderByString(s)
        finder.visit(node)
        candidates = finder.find()
        if not candidates:
            return None

        return candidates[0].node


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

    def _should_store_entry(self, extra: Union[None, object]) -> bool:
        return extra is not None and extra != []

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


class PaladinLoopFinder(GenericFinder):
    """
    A finder for While & For loops.
    """

    def visit_For(self, node) -> Any:
        """
            A visitor for For Loops.
        :param node: (ast.AST) An AST node.
        :return: None.
        """
        return True

    def visit_While(self, node: ast.While) -> Any:
        return True

    def types_to_find(self) -> Union:
        return [ast.For, ast.While]


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
        return [ast.Assign, ast.AnnAssign]

    def _add_to_assign(self, name, attr=None):
        if attr is not None:
            target_string = name + "." + str(attr)
        else:
            target_string = name

        return target_string

    def _visit_assign_type(self, node: Union[ast.Assign, ast.AnnAssign], targets: Iterable[ast.AST]):
        extras = []

        for target in targets:
            if type(target) is ast.Tuple:
                extras.extend(self.visit_Tuple(target))
            else:
                extras.append(super(GenericFinder, self).visit(target))

        # return extras
        return self._generic_visit_with_extras(node, extras)

    def visit_Call(self, node: ast.Call):
        return ast2str(node)

    def visit_Assign(self, node: ast.Assign):
        return self._visit_assign_type(node, node.targets)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        return self._visit_assign_type(node, [node.target])

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

            def visit_Constant(self, node: ast.Constant):
                return node.value

            def visit_Tuple(self, node):
                visited_elts = [self.visit(e) for e in node.elts]
                return ", ".join(["'%s'" % ve if isinstance(ve, str) else str(ve) for ve in visited_elts])

            def visit_Name(self, node):
                return node.id

            def visit_Attribute(self, node):
                return ast2str(node)  # , StubArgumentType.NAME
                # return node.attr, StubArgumentType.NAME

            def visit_Slice(self, node):
                def safe_visit(node):
                    if not node:
                        return None
                    return self.visit(node)

                return safe_visit(node.lower), safe_visit(node.upper), safe_visit(node.step)

        # Take extra for the slice.
        slice_extra = SliceFinder().visit(node.slice)
        if slice_extra is None or all(x is None for x in slice_extra):
            return [value_extra]

        # Create a subscript tuple.
        return SubscriptVisitResult(value_extra, slice_extra)

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


class FunctionCallFinder(GenericFinder):
    """
        Finds all function calls statements in the node.
    """
    TYPES_TO_EXCLUDE = [ast.FormattedValue,
                        ast.JoinedStr]

    def __init__(self) -> None:
        super().__init__()

    def types_to_find(self):
        return ast.Call

    def _is_match_paladin_stub_call(self, function_name: str) -> bool:
        return function_name.startswith('__') or function_name == 'locals' or \
               function_name == 'globals' or function_name == '__str__'

    def visit_Call(self, node: ast.Call):
        # return extras
        return self._generic_visit_with_extras(node, True)

    def visit_Name(self, node):
        # Extract name.
        name = node.id

        # Make sure its not a PaLaDiNInnerCall.
        if name in [stub.__name__ for stub in all_stubs]:
            return None

        return node.id

    def visit_Attribute(self, node):
        try:
            # Extract Name.
            name = node.value
            if type(name) is str:
                return name

            return super(GenericFinder, self).visit(name) + '.' + node.attr
            # return self.visit(name)
        except BaseException:
            print('')

    def visit_Tuple(self, node):
        extras = []
        for tuple_target in node.elts:
            extras.append(super(GenericFinder, self).visit(tuple_target))

        return tuple(extras)

    # def _should_visit(self, node: ast.AST, child_node: ast.AST) -> bool:
    #     # If the node has a field that can be extended (is a list).
    #     can_node_be_extended = [f for f in node._fields if type(node.__getattribute__(f)) == list] != []
    #
    #     # If the node should be excluded because of its type.
    #     should_node_be_excluded_by_type = type(node) in FunctionCallFinder.TYPES_TO_EXCLUDE
    #
    #     return super()._should_visit(node, child_node) \
    #            and can_node_be_extended and not should_node_be_excluded_by_type


class FunctionDefFinder(GenericFinder):

    def types_to_find(self):
        return ast.FunctionDef

    @dataclass
    class FunctionDefExtra(object):
        function_name: str
        args: list[str]

        def __init__(self):
            self.args = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        extra = FunctionDefFinder.FunctionDefExtra()
        extra.function_name = node.name
        extra.args = [arg.arg for arg in node.args.args]
        return self._generic_visit_with_extras(node, extra)


class AttributeAccessFinder(GenericFinder):

    def __init__(self):
        super().__init__()
        self.attr_accesses = []

    def types_to_find(self) -> Union[List[Type], Type]:
        return ast.Attribute

    def _should_filter(self, node: ast.AST) -> bool:
        return False

    @dataclass
    class AttributeExtra(object):
        value_extra: object
        attr_extra: object

    def _should_store_entry(self, extra: Union[None, object]) -> bool:
        return True

    # def _store_entry(self, entry: StubEntry) -> None:
    #     extra: AttributeAccessFinder.AttributeExtra = entry.extra
    #
    #     while isinstance(extra.value_extra, AttributeAccessFinder.AttributeExtra):

    def visit_Attribute(self, node: ast.Attribute):
        return self._generic_visit_with_extras(node,
                                               AttributeAccessFinder.AttributeExtra(
                                                   super(GenericFinder, self).visit(node.value),
                                                   node.attr
                                               ))

    # def visit(self, node):
    #     if isinstance(node, ast.Attribute):
    #         return super(GenericFinder, self).visit(node)
    #
    #     return node


class AugAssignFinder(GenericFinder):
    AugAssignExtra = NamedTuple('AugAssignExtra', [('op_str', str)])
    OPS = {
        ast.Add: "+",
        ast.Sub: "-",
        ast.Mult: "*",
        ast.MatMult: "@",
        ast.Div: "/",
        ast.Mod: "%",
        ast.Pow: "**",
        ast.LShift: "<<",
        ast.RShift: ">>",
        ast.BitOr: "|",
        ast.BitXor: "^",
        ast.BitAnd: "&",
        ast.FloorDiv: "//"
    }

    def types_to_find(self):
        return ast.AugAssign

    def visit_AugAssign(self, node: ast.AugAssign) -> Any:
        return AugAssignFinder.AugAssignExtra(op_str=AugAssignFinder.OPS[type(node.op)])


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


class ReturnStatementsFinder(GenericFinder):
    def types_to_find(self) -> Union:
        return ast.Return

    def visit_Return(self, node: ast.Return) -> Any:
        return self._generic_visit_with_extras(node, object())


class BreakFinder(GenericFinder):
    def types_to_find(self) -> Union:
        return ast.Break

    def visit_Break(self, node: ast.Break) -> Any:
        return self._generic_visit_with_extras(node, object())
