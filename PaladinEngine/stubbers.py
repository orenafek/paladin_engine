import ast

from conf.engine_conf import AST_LOOP_TYPES


class Stubber(ast.NodeTransformer):
    """
        An abstract basic stubber.
    """

    def __init__(self, root_module) -> None:
        """
            Constructor.
        :param root_module: (ast.Module) The root module that contains the items being stubed.
        """

        # Call the parent's constructor.
        super().__init__()

        # Set the root module.
        self.root_module = root_module

        # Set the changes map.
        self.change_map = []

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


class LoopStubber(Stubber):
    """
        TODO: doc.
    """

    def __init__(self, root_module, loop_node, stub) -> None:
        """
            Constructor
        :param root_module: (ast.module) The module that contains the loop.
        :param loop_node: (ast.stmt) The code of the loop being stubbed.
        :param stub: (AST) The stub to add as the first element of the loop's body.
        """

        # Call the super construct.
        super().__init__(root_module)

        # Init the loop's node.
        if type(loop_node) not in AST_LOOP_TYPES:
            raise NotImplementedError()

        # Set the node of the loop.
        self.loop_node = loop_node

        # Set the stub of the loop.
        self.loop_stub = stub

    def add_loop_stub(self) -> ast.Module:
        """
        # TODO: doc.
        :return:
         """
        # Extract the loop's body.
        body = self.__extract_loop_body()

        # Check if the body is a complex block or a single statement.
        if type(body) is list:
            stubed_loop_body = body
        else:
            stubed_loop_body = []

        # Add the stub.
        stubed_loop_body.insert(0, self.loop_stub)

        # Register the change.
        self._register_change(self.loop_node.body, stubed_loop_body)

        # Update the root_module.
        self.visit(self.root_module)

        return self.root_module

    def __extract_loop_body(self) -> ast.AST:
        """
            Extract the loop's body.
        :return: (AST) The loop's body.
        """
        return self.loop_node.body

    class __LoopTransformer(ast.NodeTransformer):
        pass
