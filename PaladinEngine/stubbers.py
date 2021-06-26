import ast
from abc import ABC, abstractmethod
from ast import *
from typing import Union, Any

from ast_common.ast_common import str2ast, ast2str
from finders import FinderByString
from utils.utils import assert_not_raise


class Stubber(ABC, ast.NodeTransformer):
    """
        An abstract basic stubber.
    """

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

    class _AfterStubRecord(_StubRecord):
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

    class _BeforeStubRecord(_StubRecord):
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

    class _ReplacingStubRecord(_StubRecord):
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

    def _stub(self, stub_record: _StubRecord) -> ast.Module:
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


class LoopStubber(Stubber):
    """
        A stubber of loops.
    """

    def __init__(self, root_module) -> None:
        """
            Constructor
        :param root_module: (ast.module) The module that contains the loop.
        :param loop_node: (ast.stmt) The code of the loop being stubbed.
        """
        # Call the super constructor.
        super().__init__(root_module)

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
        stub_record = Stubber._BeforeStubRecord(loop_node, container, attr_name, stub)

        # Stub.
        self._stub(stub_record)

        # Return the module.
        return self.root_module


class ForToWhilerLoopStubber(LoopStubber):
    WHILE_LOOP_TEMPLATE = \
        "__iter = {iterator}.__iter__()\n" + \
        "while True:\n" + \
        "    try:\n" + \
        "        {loop_index} = __iter.__next__()\n" + \
        "    except StopIteration:\n" + \
        "        break\n" + \
        "\n" + \
        "{body}\n"

    def __init__(self, root_module) -> None:
        super().__init__(root_module)

    def _create_while_loop_code(self, for_loop_node: ast.For):
        """

        :return:
        """

        # Extract the loop index from the for loop.
        loop_index = ast2str(for_loop_node.target)

        # Extract the collection from the for loop.
        iterator = ast2str(for_loop_node.iter)

        SPACE = ' '

        # Extract the body from the for loop.
        for_loop_body = []
        try:
            for for_loop_body_node in for_loop_node.body:
                spaces_to_add = for_loop_body_node.col_offset - for_loop_node.col_offset
                source_lines = [f'{SPACE * spaces_to_add}{line}\n'
                                for line in ast2str(for_loop_body_node, rstrip=False).split('\n')]
                for_loop_body.append(''.join(source_lines))

            for_loop_body = ''.join(for_loop_body)
        except BaseException as e:
            print(e)
        # Fill the while loop template.
        return ForToWhilerLoopStubber.WHILE_LOOP_TEMPLATE.format(iterator=iterator, loop_index=loop_index,
                                                                 body=for_loop_body)

    def stub_while_loop_instead_of_for_loop(self, for_loop_node,
                                            container: ast.AST,
                                            attr_name: str) -> ast.Module:
        # Create the while loop code.
        while_loop_code = self._create_while_loop_code(for_loop_node).replace('\t', "    ")

        # Parse to ast.
        while_loop_ast = ast.parse(while_loop_code).body

        # Create a replacing stub record.
        replacing_stub_record = Stubber._ReplacingStubRecord(for_loop_node, container, attr_name, while_loop_ast)

        return self._stub(replacing_stub_record)


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
        stub_record = Stubber._BeforeStubRecord(method_node, container, attr_name, stub)
        return self._stub(stub_record)

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
        stub_record = Stubber._AfterStubRecord(last_element_in_method, method_node, 'body', stub)
        return self._stub(stub_record)


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
            stub_record = Stubber._AfterStubRecord(assignment_node, container, attr_name, stub)
            return self._stub(stub_record)
        except BaseException as e:
            print(e)

class FunctionCallStubber(Stubber):
    def stub_func(self, node, container, attr_name, stubbed_call):
        try:
            # Create a stub record.
            stub_record = Stubber._ReplacingStubRecord(node, container, attr_name, stubbed_call)

            # Stub.
            self.root_module = self._stub(stub_record)
            assert_not_raise(ast2str, self.root_module)

            # Create a stub record.
            return self.root_module

        except BaseException as e:
            print(e)
            raise e

    def stub_function_call(self, node: ast.Call, container: ast.AST,
                           attr_name: str,
                           function_name:str,
                           args: str,
                           kwargs: str,
                           stub_function_name: str) -> Module:
        """
            Stub a function call.
        :param node:
        :param container:
        :param attr_name:
        :param stub:
        :return:
        """
        # Create the code to replace the function call itself.
        try:
            # Create a call node.
            if args != '':
                args_string = ', ' + args
            else:
                args_string = ''

            if kwargs != '':
                kwargs_string = ', ' + kwargs
            else:
                kwargs_string = ''

            stubbed_call = str2ast(f'{stub_function_name}(\'{function_name}\'{args_string}{kwargs_string})').value

            # Create a stub record.
            stub_record = Stubber._ReplacingStubRecord(node, container, attr_name, stubbed_call)

            # Stub.
            self.root_module = self._stub(stub_record)
            assert_not_raise(ast2str, self.root_module)

            # Create a stub record.
            return self.root_module

        except BaseException as e:
            print(e)
            raise e