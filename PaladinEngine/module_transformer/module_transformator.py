"""
    :file: module_transformer.py
    :brief: Transforms modules using PaLaDiN.
    :author: Oren Afek
    :since: 24/05/19
"""
import ast

import astor

from PaladinEngine.finders import PaladinInlineDefinitionFinder, AssignmentFinder, ClassDecoratorFinder
from PaladinEngine.stubbers import LoopStubber, Assign, AssignmentStubber
from PaladinEngine.stubs import __AS__, __FLI__, create_ast_stub, StubArgumentType


class ModuleTransformer(object):
    ...


class ModuleTransformer(object):
    """
        Transformations for AST modules.
    """

    def __init__(self, module: ast.AST) -> None:
        self.__module = module

    def transform_loop_invariants(self) -> ModuleTransformer:
        pidf = PaladinInlineDefinitionFinder()
        pidf.visit(self.__module)
        loops = pidf.find()

        # Take the first loop.
        loop = [l for l in loops.keys()][0]

        # Create a stub.
        # stub = create_ast_stub(__FLI__, [(loop.target.id, StubArgumentType.PLAIN)])
        stub = create_ast_stub(__FLI__, locals='locals()', globals='globals()')

        # Create a stubber.
        stubber = LoopStubber(self.__module)

        # Stub the loop invariant
        self.__module = stubber.stub_loop_invariant(loop.body[0], loop, 'body', stub)

        return self

    def transform_paladin_classes(self) -> ModuleTransformer:
        # Find all classes marked with @Paladin.
        classes_finder = ClassDecoratorFinder('Paladinize')
        classes_finder.visit(self.__module)
        marked_classes = classes_finder.find()


        print(marked_classes)

        return self

    def transform_assignments(self) -> ModuleTransformer:
        # Find all assignments.
        assignments_finder = AssignmentFinder()
        assignments_finder.visit(self.__module)
        assignments = assignments_finder.find()

        for container, attr_name, ass in assignments:
            # Create the list of the targets of the assignment.
            Assign()

            # Create a list for the assignment targets.
            targets = []

            class NameVisitor(ast.NodeVisitor):
                def visit_Name(self, node):
                    targets.append([(node.id, StubArgumentType.NAME),
                                    (node.id, StubArgumentType.ID),
                                    (node.id, StubArgumentType.PLAIN)])
                    self.generic_visit(node)

            for target in ass.targets:
                # Search for the targets in the left hand side of the assignment.
                NameVisitor().visit(target)

            # Create a stub.
            ass_stub = create_ast_stub(__AS__, *targets)

            # Create a stubber.
            ass_stubber = AssignmentStubber(self.__module)

            # Stub.
            self.__module = \
                ass_stubber.stub_after_assignment(ass, container, attr_name, ass_stub)

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
