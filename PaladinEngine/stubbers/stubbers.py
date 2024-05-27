import ast
import copy
from abc import ABC, abstractmethod
from ast import *
from typing import Union, List, cast

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import LineNo
from ast_common.ast_common import ast2str, find_closest_parent, lit2ast, wrap_str_param, str2ast
from builtin_manipulation_calls.builtin_manipulation_calls import BuiltinCollectionsUtils
from finders.finders import StubEntry, PaladinLoopFinder, ContainerFinder
from stubs.stubs import __FRAME__, __EOLI__, __SOLI__, __BMFCS__, __PRINT__, __FC__, __SOL__
from utils.utils import assert_not_raise


class Stubber(ABC, ast.NodeTransformer):
    """
        An abstract basic stubber.
    """

    _LOCALS_CALL = ast.Call(func=lit2ast(locals.__name__), args=[], keywords=[])
    _GLOBALS_CALL = ast.Call(func=lit2ast(globals.__name__), args=[], keywords=[])
    _FRAME_CALL = ast.Call(func=lit2ast(__FRAME__.__name__), args=[], keywords=[])

    ORIGINAL_LINE_NO_ATTR = '__OLN'
    ORIGINAL_END_LINE_NO_ATTR = '__OELN'

    class _StubRecord(ABC):
        """
            An abstract class for representing a stub in the AST tree.
        """

        def __init__(self,
                     original: AST,
                     container: AST,
                     attr_name: str,
                     replace: Union[AST, list]) -> None:
            """
                Constructor.
            :param original: (AST) The original AST node that will be replaced with a stub.
            :param container: (AST) The container that holds the stubbed node.
            :param attr_name: (str) The name of the attribute of the container that will be replaced.
            :param replace: (Union[AST, list[AST]) The replacement to the original content in the container.
            """
            self.original = original
            self.container = container
            self.attr_name = attr_name
            self._set_replace_list(replace)

        @abstractmethod
        def create_stub(self) -> Union[AST, list]:
            """
                Creates a stub from the original and replacements.
            :return:
            """
            raise NotImplementedError()

        def fix_locations(self) -> None:
            """
               Fixes the locations of the nodes in the ast tree.
            """
            # TODO: Needs to handle an empty container situations.

            # Extract nodes in container.
            nodes = self.container.__dict__[self.attr_name]

            if type(nodes) is not list:
                ast.copy_location(nodes, self.original)
                ast.fix_missing_locations(nodes)
                return

            # Extract the first element.
            first_element = nodes[0]

            # Fix the position of the first stubbed element.
            ast.copy_location(first_element, self.original)

            ast.fix_missing_locations(first_element)

            # Iterate over all of the items in the container that needs a fix.
            for node, node_index in zip(nodes[1:], range(1, len(nodes))):
                # Copy the location.
                ast.copy_location(node, nodes[node_index - 1])

                # Fix missing locations.
                ast.fix_missing_locations(node)

        def _set_replace_list(self, replace: Union[AST, list]) -> None:
            if type(replace) is list:
                self.replace = replace
            else:
                self.replace = [replace]

    class AfterStubRecord(_StubRecord):
        def __init__(self,
                     original: AST,
                     container: AST,
                     attr_name: str,
                     replace: Union[AST, list]) -> None:
            """
                Constructor.
            :param original: (AST) The original AST node that will be replaced with a stub.
            :param container: (AST) The container that holds the stubbed node.
            :param attr_name: (str) The name of the attribute of the container that will be replaced.
            :param replace: (Union[AST, list[AST]) The replacement to the original content in the container.
            """
            super().__init__(original, container, attr_name, replace)

        def create_stub(self) -> list:
            """
                Creates a stub with the replacement at the end.
            :return:
            """

            # Initialize a new container.
            container_with_stub = []

            # Find the original node in the container.
            for node in self.container.__dict__[self.attr_name]:
                container_with_stub.append(node)

                if node is self.original:
                    # Add the stub.
                    container_with_stub.extend(self.replace)

            return container_with_stub

    class BeforeStubRecord(_StubRecord):
        """
            A stub record for stubbing at the beginning of the container.
        """

        def __init__(self,
                     original: AST,
                     container: AST,
                     attr_name: str,
                     replace: Union[AST, list]) -> None:
            """
                Constructor.
            :param original: (AST) The original AST node that will be replaced with a stub.
            :param container: (AST) The container that holds the stubbed node.
            :param attr_name: (str) The name of the attribute of the container that will be replaced.
            :param replace: (Union[AST, list[AST]) The replacement to the original content in the container.
            """
            super().__init__(original, container, attr_name, replace)

        def create_stub(self) -> Union[AST, list]:
            """
                Creates a stub with the replacement at the end.
            :return:
            """
            containing_field = self.container.__dict__[self.attr_name]

            if type(containing_field) is ast.List:
                containing_field.elts = self.replace + containing_field.elts
                return containing_field
            elif type(containing_field) is list:
                i = containing_field.index(self.original)
                return containing_field[:i] + self.replace + containing_field[i:]
            else:
                return self.replace

    class ReplacingStubRecord(_StubRecord):
        """
            A stub record for replacing a node with another instead.
        """

        def __init__(self,
                     original: AST,
                     container: AST,
                     attr_name: str,
                     replace: Union[AST, List[AST]]) -> None:
            """
                Constructor.
            :param original: (AST) The original AST node that will be replaced with a stub.
            :param container: (AST) The container that holds the stubbed node.
            :param attr_name: (str) The name of the attribute of the container that will be replaced.
            :param replace: (Union[AST, list[AST]) The replacement to the original content in the container.
            """
            super().__init__(original, container, attr_name, replace)

        def create_stub(self) -> Union[AST, list]:
            """
                Create a stub with the replacement of original.
            :return:
            """
            try:
                containing_field = self.container.__dict__[self.attr_name]
                if type(containing_field) is ast.List:
                    containing_field.elts = self.replace[0].elts
                    return containing_field

                if type(containing_field) is list:
                    # Initialize a new container.
                    container_with_stub = []

                    for node in containing_field:
                        if node is self.original:
                            # Add the stub.
                            container_with_stub += self.replace
                        else:
                            container_with_stub.append(node)
                    return container_with_stub
                else:
                    # The containing field is not a list.
                    # TODO: Should self.container be copied before updates with stub?
                    # TODO: What if replace is more than one field?
                    return self.replace[0]
                    # assert type(self.replace) is list and len(self.replace) == 1
                    # ast.copy_location(self.replace[0], self.original)
                    # self.container.__setattr__(self.attr_name, self.replace)
                    # return self.container

            except BaseException as e:
                print(e)

    class ListReplacingStubRecord(ReplacingStubRecord):
        """
            A stub record for replacing a node with another instead.
        """

        def __init__(self,
                     original: AST,
                     container: AST,
                     attr_name: str,
                     replace: Union[AST, list]) -> None:
            """
                Constructor.
            :param original: (AST) The original AST node that will be replaced with a stub.
            :param container: (AST) The container that holds the stubbed node.
            :param attr_name: (str) The name of the attribute of the container that will be replaced.
            :param replace: (Union[AST, list[AST]) The replacement to the original content in the container.
            """
            super().__init__(original, container, attr_name, replace)

        def create_stub(self) -> Union[AST, list]:
            """
                Create a stub with the replacement of original.
            :return:
            """
            try:
                containing_field = self.container.__dict__[self.attr_name]
                if type(containing_field) is list:
                    # Initialize a new container.
                    container_with_stub = []

                    for node in containing_field:
                        if node is self.original:
                            # Add the stub.
                            container_with_stub += self.replace
                        else:
                            container_with_stub.append(node)

                    return container_with_stub

                return self.replace[0]

            except BaseException as e:
                print(e)

    def __init__(self, root_module) -> None:
        """
            Constructor.
        :param root_module: (ast.Module) The root module that contains the items being stubbed.

        """
        # Set the root module.
        self.root_module = root_module

        # Set the changes map.
        self.change_map = []

    def _register_change(self, stub_record: _StubRecord) -> None:
        """
            Register a replacement of a node.
        :param stub_record: (StubRecord) The record to stub.
        :return:
        """
        # Add to changes list.
        self.change_map.append(stub_record)

    def visit(self, node):
        """
            A visitor.
        :param node: (AST) The node that is currently visited.
        :return: None.
        """
        try:
            for stub_record in self.change_map:
                if stub_record.original is node:
                    # Replace the original with the stub.
                    stub_record.container.__dict__[stub_record.attr_name] = stub_record.create_stub()

                    # Stub.
                    stubbed = stub_record.container.__dict__[stub_record.attr_name]

                    # Fix the locations of the nodes in the ast after the stubbing.
                    stub_record.fix_locations()

                    ast.fix_missing_locations(self.root_module)

                    # Remove changes from list.
                    self.change_map.remove(stub_record)

                    self.generic_visit(node)
                    return stubbed

            self.generic_visit(node)
            return node

        except BaseException as e:
            print(e)

    def stub(self, stub_record: _StubRecord) -> ast.Module:
        """
            Stub the target node with the provided stub.
        :param stub_record: (Stubber._StubRecord) The stub record.
        :param list_positioner: ((list, stub) -> None)) A function of the form: (list_of_nodes, stub) -> None
                                                        that positions the stub in thr list of nodes.
        :param single_extractor: (list[AST]) -> AST A function of the form: list_of_nodes -> node
                                                    that extracts the single element to stub
                                                    (replaced with a list of elements).


        :return: (ast.Module) The root module of the target that has just been stubbed.
         """

        # Register the change.
        self._register_change(stub_record)

        # Update the root_module.
        self.visit(self.root_module)

        return self.root_module

    @staticmethod
    def create_ast_stub(stub, *args, **kwargs):
        """
            Create an AST node from a stub.
        :param stub: (function) A stub
        :return:
        """
        args_string = ', '.join(args)
        kwargs_string = ', '.join([f'{i[0]}={i[1]}' for i in kwargs.items()])

        arguments_string = args_string if kwargs_string == '' else \
            kwargs_string if args_string == '' else f'{args_string}, {kwargs_string}'

        # Create the call as a str.
        node = str2ast(f'{stub.__name__}({arguments_string})')
        Stubber.add_original_line_no(node, kwargs['line_no'])
        return node

    @staticmethod
    def get_original_line_no(node: ast.AST) -> LineNo:
        return getattr(node, Stubber.ORIGINAL_LINE_NO_ATTR)

    @staticmethod
    def get_original_end_line_no(node: ast.AST) -> LineNo:
        return getattr(node, Stubber.ORIGINAL_END_LINE_NO_ATTR)

    @staticmethod
    def add_original_line_no(node: ast.AST, line_no) -> ast.AST:
        setattr(node, Stubber.ORIGINAL_LINE_NO_ATTR, line_no)
        return node

    @staticmethod
    def copy_line_no(target: ast.AST, original: ast.AST):
        Stubber.add_original_line_no(target, Stubber.get_original_line_no(original))
        return target


class LoopStubber(Stubber):
    """
        A stubber of loops.
    """

    ITERATOR_NUMBER = -1

    def __init__(self, root_module) -> None:
        """
            Constructor
        :param root_module: (ast.module) The module that contains the loop.
        """
        # Call the super constructor.
        super().__init__(root_module)
        LoopStubber.ITERATOR_NUMBER += 1

    def stub_loop_invariant(self, loop_node: Union[For, While], container: AST, attr_name: str, stub: AST) -> Module:
        """
            Stub a loop invariant.
         :param loop_node: (Union[For, While]) The code of the loop being stubbed.
        :param container: (AST) The container that holds the loop node.
        :param attr_name: (str) The name of the attribute of the container that will be replaced.
        :param stub: (AST) The stub to add as the first element of the loop's body.
        :return: (ast.Module) The module containing the loop.
        """
        # Create a stub record.
        stub_record = Stubber.BeforeStubRecord(loop_node, container, attr_name, stub)

        # Stub.
        self.stub(stub_record)

        # Return the module.
        return self.root_module

    def stub_loop(self, loop_node: Union[ast.For, ast.While], container: ast.AST, attr_name: str,
                  extra: PaladinLoopFinder.PaladinLoopExtra) -> ast.Module:
        # Add a start of loop stub.
        self.stub_start_of_loop(loop_node, container, attr_name)

        # Create a loop iteration start stub.
        loop_iteration_start_stub = Stubber.copy_line_no(ast.Expr(ast.Call(func=lit2ast(__SOLI__.__name__),
                                                                           args=[lit2ast(
                                                                               Stubber.get_original_line_no(
                                                                                   loop_node)),
                                                                               Stubber._FRAME_CALL],
                                                                           keywords=[],
                                                                           )), loop_node)
        loop_node.body.insert(0, loop_iteration_start_stub)

        if isinstance(loop_node, ast.For):
            # Create a new target.
            new_for_target = Stubber.copy_line_no(cast(ast.AST, ast.Name(id=f'__iter_{LoopStubber.ITERATOR_NUMBER}')),
                                                  cast(ast.AST, loop_node))
            # Create a target assignment.
            for_target_assignment = Stubber.copy_line_no(
                ast.Assign(targets=[loop_node.target], ctx=ast.Store(), value=new_for_target), loop_node)

            # Override body.
            loop_node.body.insert(1, for_target_assignment)

            # Override target.
            self.stub(
                Stubber.ReplacingStubRecord(loop_node.target, loop_node, 'target', new_for_target))

        # Create a loop iteration end stub.
        loop_iteration_end_stub = self.create_loop_end_stub(loop_node)


        # noinspection PyTypeChecker
        loop_node.body.append(loop_iteration_end_stub)

        ast.fix_missing_locations(loop_node)
        for exitor_node in extra.breaks + extra.continues:
            cf = ContainerFinder(exitor_node)
            cf.visit(self.root_module)

            self.stub(
                Stubber.BeforeStubRecord(exitor_node, cf.container, cf.attr_name, self.create_loop_end_stub(loop_node)))

        return self.root_module

    def create_loop_end_stub(self, loop_node):
        return Stubber.copy_line_no(ast.Expr(ast.Call(func=lit2ast(__EOLI__.__name__),
                                                      args=[Stubber._FRAME_CALL],
                                                      keywords=[
                                                          ast.keyword(
                                                              arg='loop_start_line_no',
                                                              value=lit2ast(
                                                                  Stubber.get_original_line_no(
                                                                      loop_node))),
                                                          ast.keyword(
                                                              arg='loop_end_line_no',
                                                              value=lit2ast(
                                                                  Stubber.get_original_end_line_no(
                                                                      loop_node)))]
                                                      )), loop_node)

    def stub_start_of_loop(self, loop_node: Union[ast.For, ast.While], container: ast.AST, attr_name: str):
        return self.stub(Stubber.BeforeStubRecord(loop_node, container, attr_name,
                                                  cast(ast.AST, ast.Expr(value=ast.Call(func=lit2ast(__SOL__.__name__),
                                                                                        args=[Stubber._FRAME_CALL,
                                                                                              lit2ast(
                                                                                                  Stubber.get_original_line_no(
                                                                                                      loop_node))],
                                                                                        keywords=[])))))


class MethodStubber(Stubber):
    """
        A stubber of methods.
    """

    def __init__(self, root_module) -> None:
        """
            Constructor
        :param root_module: (ast.module) The module that contains the loop.
        """
        # Call the super constructor.
        super().__init__(root_module)

    def stub_precondition(self, method_node: ast.FunctionDef, container: AST, attr_name: str, stub: AST) -> Module:
        """
            Stub a precondition invariant.
        :param method_node: (ast.FunctionDef) The code of the method being stubbed.
        :param container: (AST) The container that holds the method node.
        :param attr_name: (str) The name of the attribute of the container that will be replaced.
        :param stub: (AST) The stub to add as the first element of the method's body.
        :return: (ast.Module) The module containing the method.
        """

        # Create a stub record.
        stub_record = Stubber.BeforeStubRecord(method_node, container, attr_name, stub)
        return self.stub(stub_record)

    def stub_postcondition(self, method_node: ast.FunctionDef, _, __, stub: AST) -> Module:
        """
            Stub a post-condition invariant.
        :param method_node: (ast.FunctionDef) The code of the method being stubbed.
        :param container: (AST) The container that holds the method node.
        :param attr_name: (str) The name of the attribute of the container that will be replaced.
        :param stub: (AST) The stub to add as the first element of the method's body.
        :return: (ast.Module) The module containing the method.
        """
        # Get the last element in the method.
        last_element_in_method = method_node.body[-1]

        # Create a stub record.
        stub_record = Stubber.AfterStubRecord(last_element_in_method, method_node, 'body', stub)
        return self.stub(stub_record)


class AssignmentStubber(Stubber):
    """
        A stubber for assignment statements.
    """

    def __init__(self, root_module) -> None:
        """
            Constructor
        :param root_module: (ast.module) The module that contains the assignment statement.
        """
        # Call the super constructor.
        super().__init__(root_module)

    def _extract_target(self, node):
        """
            Extract the assignment statements.
        :param node: (AST) The node to extract the assignment statement from/
        :return: (AST) The assignment statement.
        """
        if not isinstance(node, ast.Assign):
            return None

        return node

    def stub_after_assignment(self, assignment_node, container, attr_name, stub: Union[AST, list]) -> Module:
        """
            Stub an assignment.
        :param assignment_node: (ast.Assign) The assignment node.
        :param container: (AST) The container that holds the assignment node.
        :param attr_name: (str) The name of the attribute of the container that will be replaced.
        :param stub: (AST) The stub to add after the assignment.
        :return: (ast.Module) The module containing the assignment.
        """
        try:

            # Create a stub record.
            stub_record = Stubber.AfterStubRecord(assignment_node, container, attr_name, stub)
            return self.stub(stub_record)
        except BaseException as e:
            print(e)


class FunctionCallStubber(Stubber):
    def stub_func(self, node: ast.Call, container: ast.AST, attr_name: str):
        try:
            # In case of a print call, wrap with a different stub.
            if isinstance(node.func, ast.Name) and node.func.id == print.__name__:
                stub_name = __PRINT__.__name__
                stub_args = [
                    lit2ast(Stubber.get_original_line_no(node)),
                    Stubber._FRAME_CALL
                ]
            else:
                stub_name = __FC__.__name__
                stub_args = [
                    lit2ast(wrap_str_param(ast2str(node))),
                    lit2ast(ast2str(node.func)),
                    Stubber._LOCALS_CALL,
                    Stubber._GLOBALS_CALL,
                    Stubber._FRAME_CALL,
                    lit2ast(Stubber.get_original_line_no(node))
                ]

            stub_args += [ast.fix_missing_locations(a) for a in copy.deepcopy(node.args)]

            stub_kwargs = node.keywords

            stub_func_call = Stubber.copy_line_no(ast.Call(func=lit2ast(stub_name),
                                                           args=stub_args,
                                                           keywords=stub_kwargs), node)

            if isinstance(node.func, ast.Attribute) and \
                    BuiltinCollectionsUtils.is_function_suspicious_as_builtin_collection_method(node.func.attr):
                stub_func_call = FunctionCallStubber._add_suspect_builtin_manipulation_function_call_stub(
                    node.func.attr,
                    node.func.value,
                    stub_func_call,
                    node.args,
                    Stubber.get_original_line_no(node))

            # Create a stub record.
            stub_record = Stubber.ReplacingStubRecord(node, container, attr_name, stub_func_call)

            # Stub.
            self.root_module = self.stub(stub_record)
            assert_not_raise(ast2str, self.root_module)

            # Create a stub record.
            return self.root_module

        except BaseException as e:
            print(e)
            raise e

        # noinspection PyTypeChecker

    @staticmethod
    def _add_suspect_builtin_manipulation_function_call_stub(func_name: str,
                                                             caller: ast.expr,
                                                             stub_func_call: ast.Call,
                                                             args: list,
                                                             line_no: int) -> ast.Call:
        return cast(ast.Call, Stubber.add_original_line_no(ast.Call(func=lit2ast(__BMFCS__.__name__),
                                                                    args=[stub_func_call,
                                                                          caller,
                                                                          lit2ast(wrap_str_param(ast2str(caller))),
                                                                          lit2ast(wrap_str_param(func_name)),
                                                                          lit2ast(line_no),
                                                                          Stubber._FRAME_CALL,
                                                                          Stubber._LOCALS_CALL,
                                                                          Stubber._GLOBALS_CALL,
                                                                          *args
                                                                          # Must be last in case there is no arg at all.
                                                                          ],
                                                                    keywords=[]), line_no))


class FunctionDefStubber(Stubber):
    TEMP_RETURN_ASSIGMENT_VAR_NAME = '__TEMP__'

    def stub_function_def(self, node: ast.FunctionDef, container: ast.AST, attr_name, prefix_stub,
                          return_stub, return_stub_entries: List[StubEntry]) -> Module:

        if isinstance(prefix_stub, list):
            node.body = prefix_stub + node.body
        else:
            node.body = [prefix_stub] + node.body

        # If there is no return statement at the end, add one.
        if node.body != [] and not isinstance(node.body[::-1][0], ast.Return):
            return_none_stub = ast.parse('return None').body[0]
            assert isinstance(return_none_stub, ast.Return)
            node.body += [return_stub(Stubber.get_original_end_line_no(node)), return_none_stub]

        # Stub prefix and last return statement (if needed).
        stub_record = Stubber.ReplacingStubRecord(node, container, attr_name, node)
        self.root_module = self.stub(stub_record)

        # Append a return stub for each return statement.
        for rs in return_stub_entries:
            # Filter return statements of inner functions.
            if find_closest_parent(rs.node, node, ast.FunctionDef) == node:
                self.root_module = self.stub(
                    Stubber.BeforeStubRecord(rs.node, rs.container, rs.attr_name,
                                             return_stub(Stubber.get_original_line_no(rs.node))))

        return self.root_module


class AttributeAccessStubber(Stubber):
    """
        A stubber for assignment statements.
    """

    def __init__(self, root_module) -> None:
        """
            Constructor
        :param root_module: (ast.module) The module that contains the assignment statement.
        """
        # Call the super constructor.
        super().__init__(root_module)

    def stub_attribute_access(self, node: ast.Attribute,
                              container: ast.AST,
                              container_attr_name: str,
                              stub: object):
        stub_record = Stubber.ReplacingStubRecord(node, container, container_attr_name, stub)

        self.root_module = self.stub(stub_record)

        return self.root_module


class AugAssignStubber(Stubber):

    def __init__(self, root_module) -> None:
        super().__init__(root_module)
        self.temp_var_base = '____PALADIN_TEMP_AUG_ASSIGN_VAR__'
        self.temp_var_seed = 0

    def stub_aug_assigns(self, node: ast.AugAssign, container: ast.AST, container_attr_name: str):
        temp_var = self.next_temp_var(node.lineno)
        temp_op_and_assign = Stubber.copy_line_no(ast.Assign(targets=[ast.Name(id=temp_var)], ctx=ast.Store,
                                                             value=ast.BinOp(left=node.target, op=node.op,
                                                                             right=node.value)), node)
        temp_reassign = Stubber.copy_line_no(
            ast.Assign(targets=[node.target], ctx=ast.Store, value=ast.Name(id=temp_var)), node)

        stub_record = Stubber.ReplacingStubRecord(node, container, container_attr_name,
                                                  [temp_op_and_assign, temp_reassign])
        self.root_module = self.stub(stub_record)
        return self.root_module

    def next_temp_var(self, line_no: int):
        temp_var = self.temp_var_base + f'{self.temp_var_seed}__' + f'LINE_NO__{line_no}'
        self.temp_var_seed += 1
        return temp_var


class EnfOfFunctionReturnStatementStubber(Stubber):

    def __init__(self, root_module) -> None:
        super().__init__(root_module)

    def stub_end_of_function_return_statement(self, node: ast.FunctionDef, rtrn: ast.Return):
        stub_record = Stubber.AfterStubRecord(node.body[::-1][0], node, 'body', rtrn)
        self.root_module = self.stub(stub_record)
        return self.root_module


class BreakStubber(Stubber):
    def stub_breaks(self, node: ast.Break, container: ast.AST, attr_name: str, stub: ast.Call):
        stub_record = Stubber.BeforeStubRecord(node, container, attr_name, stub)
        self.stub(stub_record)
        return self.root_module
