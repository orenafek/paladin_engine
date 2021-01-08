"""
    :file: module_transformer.py
    :brief: Transforms modules using PaLaDiN.
    :author: Oren Afek
    :since: 24/05/19
"""
import ast

import astor

from PaladinEngine.finders import PaladinLoopInvariantsFinder, AssignmentFinder, \
    PaladinPostConditionFinder, DecoratorFinder
from PaladinEngine.stubbers import LoopStubber, AssignmentStubber, MethodStubber
from PaladinEngine.stubs import __AS__, __FLI__, create_ast_stub, StubArgumentType, __POST_CONDITION__
from api.api import PaladinPostCondition


class ModuleTransformer(object):
    ...


class ModuleTransformer(object):
    """
        Transformations for AST modules.
    """

    def __init__(self, module: ast.AST) -> None:
        self.__module = module

    def transform_loop_invariants(self) -> ModuleTransformer:
        pidf = PaladinLoopInvariantsFinder()
        pidf.visit(self.__module)
        loops = pidf.find()

        # Iterate over the loops.
        for loop_stub_entry in loops:
            # Create a stub.
            stub = create_ast_stub(__FLI__, locals='locals()', globals='globals()')

            # Create a stubber.
            stubber = LoopStubber(self.__module)

            # Stub the loop invariant
            self.__module = stubber.stub_loop_invariant(loop_stub_entry.extra, loop_stub_entry.node, 'body', stub)

        return self

    def transform_assignments(self) -> ModuleTransformer:
        # Find all assignments.
        assignments_finder = AssignmentFinder()
        assignments_finder.visit(self.__module)
        assignments = assignments_finder.find()

        for stub_entry in assignments:
            # Create a list for the assignment targets.
            targets = []

            class NameVisitor(ast.NodeVisitor):
                def visit_Name(self, node):
                    self._add_to_targets(node.id)
                    self.generic_visit(node)

                def visit_Attribute(self, node):
                    # Extract Name.
                    name = node.value.id
                    self._add_to_targets(name, node.attr)
                    self.generic_visit(node)

                def _add_to_targets(self, name, attr=None):
                    if attr is not None:
                        target_string = name + "." + str(attr)
                    else:
                        target_string = name

                    targets.append([(target_string, StubArgumentType.NAME), (target_string, StubArgumentType.PLAIN)])

            container = stub_entry.container
            attr_name = stub_entry.attr_name
            ass = stub_entry.node

            for target in ass.targets:
                # Search for the targets in the left hand side of the assignment.
                NameVisitor().visit(target)

            # Create a stub.
            ass_stub = create_ast_stub(__AS__, *targets, locals='locals()', globals='globals()', frame='sys._getframe(0)',
                                       line_no=f'{ass.lineno}')

            # Create a stubber.
            ass_stubber = AssignmentStubber(self.__module)

            # Stub.
            self.__module = \
                ass_stubber.stub_after_assignment(ass, container, attr_name, ass_stub)

        return self

    def transform_paladin_post_condition(self) -> ModuleTransformer:
        # Find all PaLaDiN post conditions.
        paladin_post_condition_finder = PaladinPostConditionFinder()
        paladin_post_condition_finder.visit(self.__module)
        paladin_post_conditions = paladin_post_condition_finder.find()
        for stub_entry in paladin_post_conditions:
            # Create a stub.
            post_cond_stub = create_ast_stub(__POST_CONDITION__, condition=f'"{stub_entry.extra[0].params[0]}"',
                                             locals='locals()', globals='globals()', frame='sys._getframe(0)')

            # Create a stubber.
            method_stubber = MethodStubber(self.__module)

            # Stub.
            self.__module = method_stubber.stub_postcondition(stub_entry.node,
                                                              stub_entry.container,
                                                              stub_entry.attr_name,
                                                              post_cond_stub)

        return self

    def to_code(self) -> str:
        """
            Convert the module to code.
        :return:
        """
        return astor.to_source(self.__module)

    def module(self) -> ast.AST:
        """
            Getter.
        :return: self#module
        """
        return self.__module


class PaladinPostConditionTransformer(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        # Extract decorators.
        for decorator in node.decorator_list:
            if self._decorator_predicate(node, decorator):
                self.__decorators[node] = DecoratorFinder.Decorator(node, decorator)
        self.generic_visit(node)

        # noinspection PyUnusedLocal, PyMethodMayBeStatic

    def _decorator_predicate(self, func: ast.FunctionDef, decorator: ast.expr):
        """
            A predicate to filter found decorators.
        :param decorator:  A decorator object.
        :return: True if the decorator should be added.
        """
        return DecoratorFinder.Decorator(func, decorator).name == PaladinPostCondition.__name__

