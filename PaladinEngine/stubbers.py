import ast
from abc import ABC, abstractmethod

from conf.engine_conf import AST_LOOP_TYPES


class Stubber(ABC, ast.NodeTransformer):
    """
        An abstract basic stubber.
    """

    def __init__(self, root_module, target_node, expected_target_node_types) -> None:
        """
            Constructor.
        :param root_module: (ast.Module) The root module that contains the items being stubbed.
        :param target_node: (ast.AST) The node being stubbed.
        :param expected_target_node_types: (list(class)) A list with possible expected types of the target.
        """

        # Call the parent's constructor.
        super().__init__()

        # Validate the type of the loop node.
        if type(target_node) not in expected_target_node_types:
            raise NotImplementedError()

        # Set the root module.
        self.root_module = root_module

        # Set the changes map.
        self.change_map = []

        # Set the node of the loop.
        self.target_node = target_node

    def _register_change(self, original, replacement) -> None:
        """
            Register a replacement of a node.
        :param original: (ast.AST) The node to replace.
        :param replacement: (ast.AST) The node to replace with.
        :return:
        """
        # Add to changes list.
        self.change_map.append((original, replacement))

    def visit(self, node) -> None:
        """
            A visitor.
        :param node: (ast.AST) The node that is currently visited.
        :return:
        """
        keys_for_removal = []

        for original, replacement in self.change_map:
            if node is original:
                # Copy the location into the replacement.
                ast.copy_location(replacement, original)

                # Fix the line no. and the col offset.
                ast.fix_missing_locations(replacement)

                # Remove from dict.
                keys_for_removal.append(original)

                # Remove changes from dict.
                self.change_map = [change for change in self.change_map if change[0] not in keys_for_removal]

                return replacement

    def __stub(self, stub_node, list_positioner) -> ast.Module:
        """
            Stub the target node with the provided stub.
        :param list_positioner: ((list, stub) -> None)) A function of the form: (list_of_nodes, stub) -> None
                                                        that positions the stub in thr list of nodes.
        :param stub_node: (AST) The stub to add to the target's body.

        :return: (ast.Module) The root module of the target that has just been stubbed.
         """
        # Extract the loop's body.
        body = self._extract_target_body()

        # Check if the body is a complex block or a single statement.
        if type(body) is list:
            stubbed_body = body
        else:
            stubbed_body = []

        # Add the stub.
        list_positioner(stubbed_body, stub_node)

        # Register the change.
        self._register_change(self.target_node.body, stubbed_body)

        # Update the root_module.
        self.visit(self.root_module)

        return self.root_module

    def _stub_at_beginning(self, stub_node) -> ast.Module:
        """
            Add the stub to the beginning of the target node.
        :param stub_node: (AST) The stub to add as the first element of the target's body.
        :return: (ast.Module) The root module of the target that has just been stubbed.
        """
        return self.__stub(stub_node, lambda stubbed_body, stub: stubbed_body.insert(0, stub))

    def _stub_at_end(self, stub_node) -> ast.Module:
        """
            Add the stub to the end of the target node.
        :param stub_node: (AST) The stub to add as the last element of the target's body.
        :return: (ast.Module) The root module of the target that has just been stubbed.
        """
        return self.__stub(stub_node, lambda stubbed_body, stub: stubbed_body.append(stub))

    @abstractmethod
    def _extract_target_body(self) -> ast.AST:
        """
            Extracts the body of the target node. The stub will be added to the body.
            This is an abstract method that MUST be overridden by successors.
        :return:
        """
        raise NotImplementedError()


class LoopStubber(Stubber):
    """
        A stubber of loops.
    """

    def __init__(self, root_module, loop_node) -> None:
        """
            Constructor
        :param root_module: (ast.module) The module that contains the loop.
        :param loop_node: (ast.stmt) The code of the loop being stubbed.
        """
        # Call the super constructor.
        super().__init__(root_module, loop_node, AST_LOOP_TYPES)

    def _extract_target_body(self) -> ast.AST:
        """
            Extract the loop's body.
        :return: (AST) The loop's body.
        """
        return self.target_node.body

    def stub_loop_invariant(self, stub) -> ast.Module:
        """
            Stub a loop invariant.
        :param stub: (AST) The stub to add as the first element of the loop's body.
        :return: (ast.Module) The module containing the loop.
        """
        return self._stub_at_beginning(stub)


class MethodStubber(Stubber):
    """
        A stubber of methods.
    """

    def __init__(self, root_module, method_node) -> None:
        """
            Constructor
        :param root_module: (ast.module) The module that contains the loop.
        :param method_node: (ast.stmt) The code of the method being stubbed.
        """
        # Call the super constructor.
        super().__init__(root_module, method_node, [ast.FunctionDef])

    def _extract_target_body(self) -> ast.AST:
        """
            Extract the loop's body.
        :return: (AST) The loop's body.
        """
        return self.target_node.body

    def stub_precondition(self, stub):
        """
            Stub a precondition invariant.
        :param stub: (AST) The stub to add as the first element of the method's body.
        :return: (ast.Module) The module containing the loop.
        """
        return self._stub_at_beginning(stub)

    def stub_postcondition(self, stub):
        """
            Stub a post-condition invariant.
        :param stub: (AST) The stub to add as the first element of the method's body.
        :return: (ast.Module) The module containing the loop.
        """
        return self._stub_at_end(stub)
