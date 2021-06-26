import inspect
import json
import re
from dataclasses import dataclass
from typing import Optional, Union

from archive.archive import Archive
from ast_common.ast_common import str2ast
from interactive_debugger.interactive_debugger import InteractiveDebugger

archive = Archive()



# TODO: Export tagging class.
@dataclass
class SubscriptVisitResult(object):
    collection: list
    slice: list

    def deflate(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    def __str__(self) -> str:
        return self.deflate()

    @staticmethod
    def inflate(s: dict):
        return SubscriptVisitResult(collection=s['collection'], slice=s['slice'])


def __FRAME__():
    return sys._getframe(1)


def __FLI__(locals, globals):
    """
        A stub for a for loop.
    :param locals: The local names accessible from the loop.
    :param globals: The global names accessible from the loop.
    :return:
    """
    all_vars = {**locals, **globals}

    n = all_vars['n']

    result = all_vars['result']
    error_line = '''
        if |n| >= 1:
            result >= pre(result)
        else:
            result < pre(result)'''
    try:
        values = [rv.value for rv in archive.search('result').values]

        if abs(n) >= 1:
            assert result >= all(values)
        else:
            assert result < all(values)
    except BaseException:
        pass
        # InteractiveDebugger(simple_archive, f'For Loop invariant: {error_line}\nhas been broken.', 21).cmdloop()


def handle_broken_commitment(condition, frame, line_no):
    frame_info = inspect.getframeinfo(frame)

    error_line = f'Commitment: {condition} has been broken.'
    # Initialize PaLaDinInteractiveDebugger.
    interactive_debugger = InteractiveDebugger(archive, error_line, line_no)
    interactive_debugger.cmdloop()


def __POST_CONDITION__(condition: str, frame: dict, locals, globals):
    all_vars = {**locals, **globals}

    y = all_vars['y']
    board = all_vars['self']

    def Drawn(block: Block, board: Board) -> bool:
        return block in board.grid.keys()

    def _row(grid: dict, y: int) -> list:
        return list(filter(lambda block: block[1] == y, grid))

    # noinspection PyTypeChecker
    def commitment(record: Archive.Record, line_no: int):
        # Extract the last board value from the record.
        last_board_value, last_board_line_no = record.get_last_value()

        # Extract all blocks in the grid in the row yr.
        if _row(last_board_value, y) != []:
            handle_broken_commitment(condition, frame, line_no)

    # Make a commitment.
    archive.make_commitment('self.grid', frame, commitment, all_vars)


import sys

sys._getframe(0)


def _search_in_vars_dict(symbol: Union[str, SubscriptVisitResult], vars: dict) -> Optional[object]:
    if type(symbol) is dict:
        symbol = SubscriptVisitResult.inflate(symbol)
        # Look for the collection of the subscript in the variable dictionary.
        col = symbol.collection[0][0]
        # TODO: COMPLETE ME!
        return None
        col_value = vars[col]

        subscript_key = [x[0] for x in symbol.slice]

        symbol_value = col_value.__getitem__(subscript_key)
        return symbol_value

    if symbol in vars:
        return vars[symbol]

    # The symbol is not in the variables dictionary.
    if symbol.startswith('__'):
        # The symbol is a protected member of a class.
        protected_var_with_qualifier = f'_{vars["__qualname__"]}{symbol}'

        if protected_var_with_qualifier in vars:
            return vars[protected_var_with_qualifier]

    return None


def _separate_to_container_and_func(function, expression: str, frame, vars_dict: dict) -> int:
    def _extract_identifier(s: str) -> tuple[str, str]:
        eager_func = re.match('(?P<id>.*)\\((?P<rest>.*)\\)', s)
        if eager_func:
            return eager_func.group('id'), eager_func.group('rest')

        eager_dot = re.match('(?P<id>.*)\\.(?P<rest>.*)', s)
        if eager_dot:
            return eager_dot.group('id'), eager_dot.group('rest')

    # If the call was to a __call__ function of an object, the function parameter should be of a class.
    if type(function) is type:
        container_id = id(frame)
    else:
        # Otherwise, the call was made to a function.
        # If the function is bounded, aka method, its container is the bounded object, otherwise its the frame
        # in which the call was made.
        container_id = id(function.__self__) if '__self__' in function.__dir__() else id(frame)

    return container_id

    # return _separate_to_container_and_field_inner(expression, frame, vars_dict, _extract_identifier)


def _separate_to_container_and_field(expression: str, frame, vars_dict: dict) -> tuple[int, str]:
    def separator(exr: str) -> tuple[str, str]:
        parts = exr.split('.')

        if len(parts) > 1:
            return parts[0], '.'.join(parts[1::])
        else:
            return parts[0], ''

    return _separate_to_container_and_field_inner(expression, frame, vars_dict, separator)


def _separate_to_container_and_field_inner(expression: str, frame, vars_dict: dict, separator_func) -> tuple[int, str]:
    dot_separator = '.'

    expr = expression
    container_id = id(frame)
    field = expression

    value = _search_in_vars_dict(field, vars_dict)

    while dot_separator in expr:
        identifier, rest = separator_func(expr)
        field = identifier
        obj = vars_dict[identifier]
        container_id = id(obj)
        expr = rest

    return container_id, field


def __AS__(expression: str, target: str, locals: dict, globals: dict, frame, line_no: int) -> None:
    # Create variable dict.
    vars_dict = {**locals, **globals}

    container_id, field = _separate_to_container_and_field(target, frame, vars_dict)

    value = _search_in_vars_dict(field, vars_dict)

    if value is None:
        # TODO: handle?
        return

    # Create Record key.
    record_key = Archive.Record.RecordKey(container_id, field)

    # Create Record value.
    record_value = Archive.Record.RecordValue(type(value), value, expression, line_no)

    archive.store(record_key, record_value)


def __FC__(expression: str, function,
           locals: dict, globals: dict, frame, line_no: int,
           *args: Optional[list[object]], **kwargs: Optional[dict[object]]):
    """
        Store function call stub.
    :param function: The function that was called.
    :param locals: Dictionary with the local variables of the calling context.
    :param globals: Dictionary with the global variables of the calling context.
    :param frame: The stack frame of the calling context
    :param line_no: The line no of the function call.
    :param args: The arguments passed to the function.
    :param kwargs: The keyword arguments passed to the function.
    :return: None.
    """

    vars_dict = {**locals, **globals}

    # Function type.
    func_type = type(lambda _: _)

    # Call the function.
    ret_value = function(*args, **kwargs)

    # Find container.
    container_id = _separate_to_container_and_func(function, expression, frame, vars_dict)

    args_string = ', '.join([str(a) for a in args])
    kwargs_string = ', '.join(f"{t[0]}={t[1]}" for t in kwargs.items())

    # Create an extra with the args and keywords.
    extra = f'args = {args_string}, kwargs = {kwargs_string}'

    # Create a Record key.
    record_key = Archive.Record.RecordKey(container_id, function.__name__)

    # Create Record value.
    record_value = Archive.Record.RecordValue(func_type, ret_value, expression, line_no, extra)

    # Store.
    archive.store(record_key, record_value)

    # Return ret value.
    return ret_value


def __FCS__(name: str,
            args: list,
            kwargs: list,
            return_value: object,
            locals: dict, globals: dict, frame: dict, line_no: int) -> None:
    """
        A stub for function calls.
        :param function_name:               The name of the function.
        :param function_args_kwargs:        A list of the args and kwargs of the function.
        :param function_call_return_value   The return value of the call to this function.
        :param locals                       A dict of the local variables of the context in which this stub was called.
        :param globals                      A dict of the global variables of the context in which this stub was called.
        :param frame                        The frame of the context in which this stub was called.
        :param line_no                      The line number in the original source code that triggered the creation of this
                                            stub.

    :return: None
    """

    # Create a function call record value.
    function_call_record_value = archive.Record.FunctionCallRecordValue(
        return_value,
        line_no,
        args,
        kwargs)

    # Store the function call.
    archive.store(name, frame, line_no, function_call_record_value, vars_dict={**locals, **globals})


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
    return str2ast(f'{stub.__name__}({arguments_string})')


all_stubs = [__FLI__, __AS__, __FCS__]


class StubArgumentType(enumerate):
    """
        Types of arguments to stubs.
    """

    # Pass the argument "as is."
    # e.g.: if a stub stubs the statement: print(x)
    #       and the value of x should be passed to the stub,
    #       the stub will be: __STUB_PRINT(x)
    PLAIN = 0

    # Pass the argument's name.
    # e.g.: if a stub stubs the statement: print(x)
    #       and the name of x should be passed to the stub,
    #       the stub will be: __STUB_PRINT('x')
    NAME = 1

    # Pass the argument's id.
    # e.g.: if a stub stubs the statement: print(x)
    #       and the id of x should be passed to the stub,
    #       the stub will be: __STUB_PRINT(id(x))
    ID = 2
