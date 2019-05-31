import ast
from abc import ABC, abstractmethod
from ast import *
from typing import Union


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
            self.replace = replace

        @abstractmethod
        def create_stub(self) -> Union[AST, list]:
            """
                Creates a stub from the original and replacements.
            :return:
            """
            raise NotImplementedError()

        @abstractmethod
        def fix_locations(self) -> None:
            """
                Fixes the locations of the nodes in the ast tree.
            """
            raise NotImplementedError()

    class _EndStubRecord(_StubRecord):
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
                    container_with_stub.append(self.replace)

            return container_with_stub

        def fix_locations(self) -> None:
            """
                Fixes the locations of the nodes in the ast tree.
            """
            # TODO: Implement?
            pass

    class _BeginningStubRecord(_StubRecord):
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

            # Initialize a new container.
            container_with_stub = []

            # Find the original node in the container.
            for node in self.container.__dict__[self.attr_name]:
                if node is self.original:
                    # Add the stub.
                    container_with_stub.append(self.replace)

                container_with_stub.append(node)

            return container_with_stub

        def fix_locations(self):

            # TODO: Needs to handle an empty container situations.

            # Extract nodes in container.
            nodes = self.container.__dict__[self.attr_name]

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

    def visit(self, node) -> None:
        """
            A visitor.
        :param node: (AST) The node that is currently visited.
        :return: None.
        """
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
        stub_record = Stubber._BeginningStubRecord(loop_node, container, attr_name, stub)

        # Stub.
        self._stub(stub_record)

        # Return the module.
        return self.root_module


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
        stub_record = Stubber._BeginningStubRecord(method_node, container, attr_name, stub)
        return self._stub(stub_record)

    def stub_postcondition(self, method_node: ast.FunctionDef, container: AST, attr_name: str, stub: AST) -> Module:
        """
            Stub a post-condition invariant.
        :param method_node: (ast.FunctionDef) The code of the method being stubbed.
        :param container: (AST) The container that holds the method node.
        :param attr_name: (str) The name of the attribute of the container that will be replaced.
        :param stub: (AST) The stub to add as the first element of the method's body.
        :return: (ast.Module) The module containing the method.
        """
        # Create a stub record.
        stub_record = Stubber._EndStubRecord(method_node, container, attr_name, stub)
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

        # Create a stub record.
        stub_record = Stubber._EndStubRecord(assignment_node, container, attr_name, stub)
        return self._stub(stub_record)

    def stub_assignment_with_tmp(self):

        class _with_tmp_(Stubber._StubRecord):
            """
                A stub record for stubbing with tmp.
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

                # Initialize a new container.
                container_with_stub = []

                # Find the original node in the container.
                for node in self.container.__dict__[self.attr_name]:
                    if node is self.original:
                        # Add the stub.
                        container_with_stub.append(self.replace)

                    container_with_stub.append(node)

                return container_with_stub

            def fix_locations(self):

                # TODO: Needs to handle an empty container situations.

                # Extract nodes in container.
                nodes = self.container.__dict__[self.attr_name]

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
