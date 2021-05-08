"""
    :file: module_transformer.py
    :brief: Transforms modules using PaLaDiN.
    :author: Oren Afek
    :since: 24/05/19
"""
import ast
import os

import astor

from PaladinEngine.finders import PaladinForLoopInvariantsFinder, AssignmentFinder, \
    PaladinPostConditionFinder, DecoratorFinder, PaladinForLoopFinder, StubEntry, FunctionCallFinder, GenericFinder
from PaladinEngine.stubbers import LoopStubber, AssignmentStubber, MethodStubber, ForToWhilerLoopStubber, \
    FunctionCallStubber
from PaladinEngine.stubs import __AS__, __FLI__, create_ast_stub, StubArgumentType, __POST_CONDITION__, __FCS__
from PaladinEngine.api.api import PaladinPostCondition


class ModuleTransformer(object):
    ...


class ModuleTransformer(object):
    """
        Transformations for AST modules.
    """

    def __init__(self, module: ast.AST) -> None:
        self._module = module
        self.__temp_var_counter = 0

    def transform_loop_invariants(self) -> ModuleTransformer:
        pidf = PaladinForLoopInvariantsFinder()
        pidf.visit(self._module)
        loops = pidf.find()

        # Iterate over the loops.
        for loop_stub_entry in loops:
            # Create a stub.
            stub = create_ast_stub(__FLI__, locals='locals()', globals='globals()')

            # Create a stubber.
            stubber = LoopStubber(self._module)

            # Stub the loop invariant
            self._module = stubber.stub_loop_invariant(loop_stub_entry.extra, loop_stub_entry.node, 'body', stub)

        return self

    def transform_for_loops_to_while_loops(self) -> ModuleTransformer:
        plf = PaladinForLoopFinder()
        plf.visit(self._module)
        for_loop_entries = plf.find()

        for for_loop_entry in for_loop_entries:
            # Create a stuber.
            stuber = ForToWhilerLoopStubber(self._module)

            # Stub.
            self._module = stuber.stub_while_loop_instead_of_for_loop(for_loop_entry.node,
                                                                      for_loop_entry.container,
                                                                      for_loop_entry.attr_name)
        return self

    def transform_assignments(self) -> ModuleTransformer:
        try:
            # Find all assignments.
            assignments_finder = AssignmentFinder()
            assignments_finder.visit(self._module)
            assignments = assignments_finder.find()

            for stub_entry in assignments:
                # Create a list for the assignment targets.
                container = stub_entry.container
                attr_name = stub_entry.attr_name
                ass = stub_entry.node
                targets = stub_entry.extra

                # Create a stub.
                ass_stub = create_ast_stub(__AS__, *targets, locals='locals()', globals='globals()',
                                           frame='sys._getframe(0)',
                                           line_no=f'{ass.lineno}')

                # Create a stubber.
                ass_stubber = AssignmentStubber(self._module)

                # Stub.
                self._module = \
                    ass_stubber.stub_after_assignment(ass, container, attr_name, ass_stub)

            return self
        except BaseException as e:
            print(e)

    def transform_paladin_post_condition(self) -> ModuleTransformer:
        # Find all PaLaDiN post conditions.
        paladin_post_condition_finder = PaladinPostConditionFinder()
        paladin_post_condition_finder.visit(self._module)
        paladin_post_conditions = paladin_post_condition_finder.find()
        for stub_entry in paladin_post_conditions:
            # Create a stub.
            post_cond_stub = create_ast_stub(__POST_CONDITION__,
                                             condition=f'{stub_entry.extra.name}({", ".join(stub_entry.extra.params)})',
                                             locals='locals()', globals='globals()', frame='sys._getframe(0)')

            # Create a stubber.
            method_stubber = MethodStubber(self._module)

            # Stub.
            self._module = method_stubber.stub_postcondition(stub_entry.node,
                                                             stub_entry.container,
                                                             stub_entry.attr_name,
                                                             post_cond_stub)

        return self

    def transform_function_calls(self) -> ModuleTransformer:
        i = 0
        try:
            # Find all function calls.
            function_call_finder = FunctionCallFinder()
            function_call_finder.visit(self._module)
            function_calls = function_call_finder.find()
            while function_calls:
                stub_entry = function_calls[0]
                # Create a temp var to hold the return value of the function call.
                temp_return_value_var = f'____{i}'

                # Convert function name to a string.
                function_name_string = f'\'{stub_entry.extra.function_name}\''

                # Convert args to a string.
                args_string = '[' + ', '.join([f'\'{a}\'' for a in stub_entry.extra.args if not isinstance(a, str)] +
                                              [f'{a}' for a in stub_entry.extra.args if isinstance(a, str)]) + ']'

                # Converto kwargs to a string.
                kwargs_string = '[' + ', '.join([str(t) for t in stub_entry.extra.kwargs.items()]) + ']'

                # Create a stub.
                function_call_stub = create_ast_stub(__FCS__,
                                                     name=function_name_string,
                                                     args=args_string,
                                                     kwargs=kwargs_string,
                                                     return_value=temp_return_value_var,
                                                     frame='sys._getframe(0)',
                                                     locals='locals()',
                                                     globals='globals()',
                                                     line_no=f'{stub_entry.node.lineno}')

                function_call_stubber = FunctionCallStubber(self._module, temp_return_value_var, stub_entry.node)

                container_attr_name_in_container_of_container = GenericFinder.get_node_attr_name(
                    stub_entry.extra.container_of_container, stub_entry.container)

                self._module = function_call_stubber.stub_function_call(stub_entry.node,
                                                                        stub_entry.container,
                                                                        stub_entry.extra.container_of_container,
                                                                        stub_entry.attr_name,
                                                                        container_attr_name_in_container_of_container,
                                                                        function_call_stub)
                path = f'output.py'
                if os.path.exists(path):
                    os.remove(path)
                with open(path, 'w+') as f:
                    s = ast.unparse(self._module)
                    f.write(s)
                    f.close()
                i += 1

                function_call_finder = FunctionCallFinder()
                function_call_finder.visit(self._module)
                function_calls = function_call_finder.find()

        except BaseException as e:
            print(f'i = {i} {e}')
        return self

    def to_code(self) -> str:
        """
            Convert the module to code.
        :return:
        """
        return ast.unparse(self._module).strip()

    def module(self) -> ast.AST:
        """
            Getter.
        :return: self#module
        """
        return self._module


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
