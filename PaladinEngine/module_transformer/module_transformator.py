"""
    :file: module_transformer.py
    :brief: Transforms modules using PaLaDiN.
    :author: Oren Afek
    :since: 24/05/19
"""
import ast
import textwrap
import traceback

from api.api import PaladinPostCondition
from finders.finders import PaladinForLoopInvariantsFinder, AssignmentFinder, \
    PaladinPostConditionFinder, DecoratorFinder, PaladinForLoopFinder, FunctionCallFinder
from stubbers.stubbers import LoopStubber, AssignmentStubber, MethodStubber, ForToWhilerLoopStubber, \
    FunctionCallStubber
from stubs.stubs import __FLI__, create_ast_stub, __POST_CONDITION__, __AS__, __FC__, __FRAME__
from ast_common.ast_common import ast2str, str2ast, wrap_str_param


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
                for target in targets:
                    ass_stub = create_ast_stub(__AS__,
                                               wrap_str_param(ast2str(stub_entry.node)),
                                               wrap_str_param(target),
                                               locals='locals()',
                                               globals='globals()',
                                               frame=__FRAME__.__name__,
                                               line_no=f'{ass.lineno}')

                    # Create a stubber.
                    ass_stubber = AssignmentStubber(self._module)

                    # Stub.
                    self._module = \
                        ass_stubber.stub_after_assignment(ass, container, attr_name, ass_stub)

            return self
        except BaseException as e:
            traceback.print_exception(e)
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
                                             locals='locals()', globals='globals()', frame=__FRAME__.__name__)

            # Create a stubber.
            method_stubber = MethodStubber(self._module)

            # Stub.
            self._module = method_stubber.stub_postcondition(stub_entry.node,
                                                             stub_entry.container,
                                                             stub_entry.attr_name,
                                                             post_cond_stub)

        return self

    def transform_function_calls(self) -> ModuleTransformer:
        try:
            # Find all function calls.
            function_call_finder = FunctionCallFinder()
            function_call_finder.visit(self._module)
            function_calls = function_call_finder.find()

            # Create a stubber.
            function_call_stubber = FunctionCallStubber(self._module)

            for stub_entry in function_calls:
                # Convert args to a string.
                args_string = ", ".join(stub_entry.extra.args)

                # Convert kwargs to a string.
                kwargs_string = ', '.join([f'{t[0]}={t[1]}' for t in stub_entry.extra.kwargs.items()])

                all_args_string = args_string

                if kwargs_string != '':
                    all_args_string += ', ' + kwargs_string

                s = f'{__FC__.__name__}(' + ', '.join([
                    f'\'{ast2str(stub_entry.node)}\'',
                    f'{ast2str(stub_entry.node.func)}',
                    'locals()',
                    'globals()',
                    __FRAME__.__name__,
                    f'{stub_entry.node.lineno}',
                    f'{all_args_string}' if args_string else '']) + \
                    ')'

                # Create a stub.
                stubbed_call = str2ast(s).value

                # func_stub = create_ast_stub(__AS_FC__,
                #                             ast2str(stub_entry.node),
                #                             stub_entry.node.func,
                #                             stub_entry.container,
                #                             locals='locals()',
                #                             globals='globals()',
                #                             frame=__FRAME__.__name,
                #                             line_no=stub_entry.node.lineno,
                #                             args=args_string,
                #                             kwargs=kwargs_string)

                self.module = function_call_stubber.stub_func(stub_entry.node, stub_entry.container,
                                                              stub_entry.attr_name, stubbed_call)

        except BaseException as e:
            print(e)

        finally:
            return self

    @property
    def module(self) -> ast.AST:
        """
            Getter.
        :return: self#module
        """
        return self._module

    @module.setter
    def module(self, value):
        self._module = value


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
