"""
    :file: module_transformer.py
    :brief: Transforms modules using PaLaDiN.
    :author: Oren Afek
    :since: 24/05/19
"""
import ast
from typing import List, cast

from ast_common.ast_common import ast2str, wrap_str_param, lit2ast
from finders.finders import PaladinForLoopInvariantsFinder, AssignmentFinder, \
    PaladinPostConditionFinder, PaladinLoopFinder, FunctionCallFinder, FunctionDefFinder, \
    AttributeAccessFinder, AugAssignFinder, StubEntry, ReturnStatementsFinder, BreakFinder
from stubbers.stubbers import LoopStubber, AssignmentStubber, MethodStubber, \
    FunctionCallStubber, FunctionDefStubber, AttributeAccessStubber, AugAssignStubber, BreakStubber, Stubber
from stubs.stubs import __FLI__, __POST_CONDITION__, __AS__, __ARG__, __DEF__, \
    __UNDEF__, __AC__, __PIS__, __BREAK__


class ModuleTransformer(object):
    """
        Transformations for AST modules.
    """

    def __init__(self, module: ast.AST) -> None:
        self._module = module
        self._store_original_line_no()
        self.__temp_var_counter = 0

    def transform_loop_invariants(self) -> 'ModuleTransformer':
        pidf = PaladinForLoopInvariantsFinder()
        pidf.visit(self._module)
        loops = pidf.find()

        # Iterate over the loops.
        for loop_stub_entry in loops:
            # Create a stub.
            stub = Stubber.create_ast_stub(__FLI__,
                                           locals='locals()', globals='globals()',
                                           line_no=Stubber.get_original_line_no(loop_stub_entry.node))

            # Create a stubber.
            stubber = LoopStubber(self._module)

            # Stub the loop invariant
            self._module = stubber.stub_loop_invariant(loop_stub_entry.extra, loop_stub_entry.node, 'body', stub)

        return self

    def transform_loops(self) -> 'ModuleTransformer':
        plf = PaladinLoopFinder()
        plf.visit(self._module)
        loop_entries = plf.find()

        while loop_entries:
            loop_entry = loop_entries.pop()

            # Create a stubber.
            stubber = LoopStubber(self._module)

            # Stub.
            self._module = stubber.stub_loop(loop_entry.node, loop_entry.container, loop_entry.attr_name)

            plf.visit(self._module)
            loop_entries = plf.find()

        return self

    def transform_assignments(self) -> 'ModuleTransformer':
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
                    ass_stub = Stubber.create_ast_stub(__AS__,
                                                       wrap_str_param(
                                                           ast2str(stub_entry.node).replace('"', '@').replace("'",
                                                                                                              "@")),
                                                       wrap_str_param(str(target)),
                                                       locals='locals()',
                                                       globals='globals()',
                                                       frame='__FRAME__()',
                                                       line_no=f'{Stubber.get_original_line_no(stub_entry.node)}')

                    # Create a stubber.
                    ass_stubber = AssignmentStubber(self._module)

                    # Stub.
                    self._module = \
                        ass_stubber.stub_after_assignment(ass, container, attr_name, ass_stub)

            return self
        except BaseException as e:
            print(e)
            raise e

    def transform_function_def(self) -> 'ModuleTransformer':
        # Find all function definitions.
        function_def_finder = FunctionDefFinder()
        function_def_finder.visit(self._module)
        function_defs: List[StubEntry] = function_def_finder.find()

        for function_def in function_defs:
            original_line_no = Stubber.get_original_line_no(function_def.node)
            function_def_stub = Stubber.create_ast_stub(__DEF__,
                                                        wrap_str_param(function_def.extra.function_name),
                                                        line_no=f'{original_line_no}',
                                                        frame='__FRAME__()')

            # Create a stubber.
            function_def_stubber = FunctionDefStubber(self._module)

            prefix_stubs = [function_def_stub]

            if function_def.extra.function_name == '__init__':
                # Add a __PIS__ stub.
                # First param should be the object being initialized (usually "self").
                first_arg = function_def.extra.args[0]
                init_prefix_stub = Stubber.create_ast_stub(__PIS__,
                                                           first_arg,
                                                           wrap_str_param(first_arg),
                                                           line_no=f'{original_line_no}')
                prefix_stubs.append(init_prefix_stub)
            # Create args prefix_stubs.

            for arg in function_def.extra.args:
                arg_stub = Stubber.create_ast_stub(__ARG__,
                                                   wrap_str_param(function_def.extra.function_name),
                                                   wrap_str_param(arg),
                                                   arg,
                                                   locals='locals()',
                                                   globals='globals()',
                                                   frame='__FRAME__()',
                                                   line_no=f'{original_line_no}', )
                prefix_stubs.append(arg_stub)

            # Create suffix stub.
            suffix_stub = lambda rsln: Stubber.copy_line_no(
                cast(ast.AST, ast.Expr(ast.Call(func=lit2ast(__UNDEF__.__name__),
                                                args=[lit2ast(wrap_str_param(function_def.extra.function_name)),
                                                      Stubber._FRAME_CALL,
                                                      lit2ast(rsln)],
                                                keywords=[]
                                                ))), function_def.node)

            # Find all return statements.
            return_statement_finder = ReturnStatementsFinder()
            return_statement_finder.visit(function_def.node)
            return_statements = return_statement_finder.find()

            # Stub.
            self._module = function_def_stubber.stub_function_def(function_def.node, function_def.container,
                                                                  function_def.attr_name,
                                                                  prefix_stubs,
                                                                  suffix_stub, return_statements)

        return self

    def transform_paladin_post_condition(self) -> 'ModuleTransformer':
        # Find all PaLaDiN post conditions.
        paladin_post_condition_finder = PaladinPostConditionFinder()
        paladin_post_condition_finder.visit(self._module)
        paladin_post_conditions = paladin_post_condition_finder.find()
        for stub_entry in paladin_post_conditions:
            # Create a stub.
            post_cond_stub = Stubber.create_ast_stub(__POST_CONDITION__,
                                                     condition=f'{stub_entry.extra.name}({", ".join(stub_entry.extra.params)})',
                                                     locals='locals()', globals='globals()', frame='__FRAME__()',
                                                     line_no=Stubber.get_original_line_no(stub_entry.node))

            # Create a stubber.
            method_stubber = MethodStubber(self._module)

            # Stub.
            self._module = method_stubber.stub_postcondition(stub_entry.node,
                                                             stub_entry.container,
                                                             stub_entry.attr_name,
                                                             post_cond_stub)

        return self

    def transform_function_calls(self) -> 'ModuleTransformer':
        try:
            # Find all function calls.
            function_call_finder = FunctionCallFinder()
            function_call_finder.visit(self._module)
            function_calls = function_call_finder.find()

            # Create a stubber.
            function_call_stubber = FunctionCallStubber(self._module)

            for stub_entry in function_calls:
                # TODO: Patch for dataclasses support.
                if 'field(default_factory' in ast2str(stub_entry.node):
                    function_calls.pop(0)
                    continue

                self.module = function_call_stubber.stub_func(stub_entry.node, stub_entry.container,
                                                              stub_entry.attr_name)

        except BaseException as e:
            print(e)

        finally:
            return self

    def transform_attribute_accesses(self) -> 'ModuleTransformer':
        try:
            # Find all attribute accesses.
            attribute_finder = AttributeAccessFinder()
            attribute_finder.visit(self.module)
            attribute_accesses = attribute_finder.find()

            # Create a stubber.
            attribute_access_stubber = AttributeAccessStubber(self.module)

            while attribute_accesses:
                attr_acc = attribute_accesses[0]

                # In case that the attribute access is a lhs,
                # TODO: Handle lhs.
                if isinstance(attr_acc.container, ast.Assign) and attr_acc.node in attr_acc.container.targets:
                    # TODO: Currently skipping.
                    attribute_accesses = attribute_accesses[1::]
                    continue
                else:
                    attr_acc_stub = Stubber.create_ast_stub(__AC__,
                                                            ast2str(attr_acc.node.value),
                                                            wrap_str_param(attr_acc.node.attr),
                                                            wrap_str_param(ast2str(attr_acc.node)),
                                                            locals='locals()',
                                                            globals='globals()',
                                                            line_no=Stubber.get_original_line_no(attr_acc.node))

                    self.module = attribute_access_stubber.stub_attribute_access(
                        attr_acc.node,
                        attr_acc.container,
                        attr_acc.attr_name,
                        attr_acc_stub.value
                    )

                # Find all function calls.
                attribute_finder = AttributeAccessFinder()
                attribute_finder.visit(self.module)
                attribute_accesses = attribute_finder.find()

        except BaseException as e:
            print(e)

        finally:
            return self

    def transform_aug_assigns(self) -> 'ModuleTransformer':
        try:
            # Find all aug assigns.
            aug_assign_finder = AugAssignFinder()
            aug_assign_finder.visit(self.module)

            aug_assigns = aug_assign_finder.find()

            # Create a stubber.
            aug_assign_stubber = AugAssignStubber(self.module)

            for aug_assign in aug_assigns:
                self.module = aug_assign_stubber.stub_aug_assigns(aug_assign.node, aug_assign.container,
                                                                  aug_assign.attr_name)

        except BaseException as e:
            print(e)

        finally:
            return self

    def transform_breaks(self) -> 'ModuleTransformer':
        try:
            # Find all breaks.
            breaks_finder = BreakFinder()
            breaks_finder.visit(self.module)

            breaks = breaks_finder.find()
            for stub_entry in breaks:
                # Create a stub.
                break_stub = Stubber.create_ast_stub(__BREAK__,
                                                     frame='__FRAME__()',
                                                     line_no=f'{Stubber.get_original_line_no(stub_entry.node)}')
                # Create a stubber.
                break_stuuber = BreakStubber(self.module)
                self.module = break_stuuber.stub_breaks(stub_entry.node, stub_entry.container, stub_entry.attr_name,
                                                        break_stub)

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

    def _store_original_line_no(self):
        class _Transformer(ast.NodeTransformer):
            def visit(self, node: ast.AST):
                setattr(node, Stubber.ORIGINAL_LINE_NO_ATTR, node.lineno if hasattr(node, 'lineno') else -1)
                setattr(node, Stubber.ORIGINAL_END_LINE_NO_ATTR, node.end_lineno if hasattr(node, 'end_lineno') else -1)
                return super().visit(node)

        self.module = _Transformer().visit(self.module)
