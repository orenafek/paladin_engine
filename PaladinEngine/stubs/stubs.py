import abc
import ast
import functools
import re
import sys
from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from typing import Optional, Union, TypeVar, Tuple, List, Dict, Set, Iterable, Collection, Callable

from archive.archive import Archive
from ast_common.ast_common import str2ast, ast2str
from builtin_manipulation_calls.builtin_manipulation_calls import IS_BUILTIN_MANIPULATION_FUNCTION_CALL
from common.common import POID, PALADIN_OBJECT_COLLECTION_FIELD, PALADIN_OBJECT_COLLECTION_EXPRESSION, ISP

archive = Archive()


# TODO: Export tagging class.
@dataclass
class SubscriptVisitResult(object):
    collection: str
    slice: tuple

    def __str__(self):
        if type(self.slice) is not tuple:
            keys = str(self.slice)
        else:
            keys = '' if len(self.slice) == 0 else str(self.slice[0]) if len(self.slice) == 1 else \
                ":".join([str(x) if x else "" for x in self.slice])
        return f'{self.collection}[{keys}]'


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


def handle_broken_commitment(condition, frame, line_no):
    pass


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
    if type(function) in [type, abc.ABCMeta]:
        container_id = id(frame)
    else:
        # Otherwise, the call was made to a function.
        # If the function is bounded, aka method, its container is the bounded object, otherwise its the frame
        # in which the call was made.
        container_id = id(function.__self__) if '__self__' in function.__dir__() else id(frame)

    return container_id

    # return _separate_to_container_and_field_inner(expression, frame, vars_dict, _extract_identifier)


def _separate_to_container_and_field(expression: str, frame, locals: dict, globals: dict) -> tuple[
    int, str, object, bool]:
    expression_ast = str2ast(expression).value
    if isinstance(expression_ast, ast.Subscript):
        getitem_arg = f'''{slice.__name__}(start={ast2str(expression_ast.slice.lower)},
                                           stop={ast2str(expression_ast.slice.upper)},
                                           step={ast2str(expression_ast.slice.step)})
                       ''' if isinstance(expression_ast.slice, ast.Slice) else eval(ast2str(expression_ast.slice),
                                                                                    globals, locals)
        subscript_value = eval(ast2str(expression_ast.value), globals, locals)
        return id(subscript_value), getitem_arg, eval(expression, globals, locals), True

    if not isinstance(expression_ast, ast.Attribute):
        # There is only an object.
        value = eval(expression, globals, locals)
        return id(frame), expression, value, True

    container = eval(ast2str(expression_ast.value), globals, locals)
    field = expression_ast.attr if type(expression_ast.attr) is str else ast2str(expression_ast.attr)

    return id(container), field, container, False


def __DEF__(func_name: str, line_no: int, frame):
    archive.store_new \
        .key(id(frame), func_name, __DEF__.__name__) \
        .value(type(lambda _: _), func_name, func_name, line_no)


def __PIS__(first_param: object, first_param_name: str, line_no: int):
    # TODO: Should type(first_param) be int instead?
    archive.store_new \
        .key(Archive.GLOBAL_PALADIN_CONTAINER_ID, first_param_name, __PIS__.__name__) \
        .value(type(first_param), id(first_param), first_param_name, line_no)


def __UNDEF__(func_name: str, line_no: int, frame):
    archive.store_new \
        .key(id(frame), func_name, __UNDEF__.__name__) \
        .value(type(lambda _: _), func_name, func_name, line_no)


def __ARG__(func_name: str, arg: str, value: object, locals: dict, globals: dict, frame,
            line_no: int):
    archive.store_new \
        .key(id(frame), arg, __ARG__.__name__) \
        .value(type(value), value, arg, line_no)

    if func_name == '__init__' and arg == 'self':
        # FIXME: Handling only cases when __init__ is called as __init__(self [,...]),
        # FIXME: Meaning that if __init__ is called with a firs arg which is not "self", this wouldn't work.
        archive.store_new \
            .key(id(frame), PALADIN_OBJECT_COLLECTION_FIELD, __AS__.__name__) \
            .value(type(value), value, PALADIN_OBJECT_COLLECTION_EXPRESSION, line_no)


def __AS__(expression: str, target: str, locals: dict, globals: dict, frame, line_no: int) -> None:
    if not archive.should_record:
        return

    container_id, field, container, is_container_value = _separate_to_container_and_field(target, frame, locals,
                                                                                          globals)
    value = container if is_container_value else container.__getattribute__(
        field) if field in container.__dict__ else None
    if value is None:
        # TODO: handle?
        return

    __store(container_id, field, line_no, target, value)


def __store(container_id, field, line_no, target, value, _time: Optional[int] = None,
            kind: Archive.Record.StoreKind = Archive.Record.StoreKind.VAR):
    value_to_store = POID(value)
    rv = archive.store_new \
        .key(container_id, field, __AS__.__name__, kind) \
        .value(type(value), value_to_store, target, line_no)

    if _time:
        rv.time = _time

    def _store_inner(v: object) -> None:
        if ISP(type(v)) or not v:
            return None

        if type(v) in [list, tuple, set]:
            return _store_lists_tuples_and_sets(v)

        if type(v) is dict:
            return _store_dicts(id(v), v)

        return _store_dicts(id(v), v.__dict__)

    def _store_lists_tuples_and_sets(v: Union[List, Tuple, Set]):
        for index, item in enumerate(v):
            irv = archive.store_new \
                .key(id(v), index, __AS__.__name__, Archive.Record.StoreKind.kind_by_type(type(v))) \
                .value(type(item), POID(item), f'{type(v)}[{index}]', line_no)

            irv.time = rv.time
            _store_inner(item)

    def _store_dicts(d_id: int, d: Dict):
        for k, v in d.items():
            irv = archive.store_new \
                .key(d_id, POID(k), __AS__.__name__, Archive.Record.StoreKind.DICT_ITEM) \
                .value(type(v), POID(v), f'{id(d)}[{POID(k)}] = {POID(v)}', line_no)

            irv.time = rv.time
            _store_inner(k)
            _store_inner(v)

    _store_inner(value)


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

    # Find container.
    container_id = _separate_to_container_and_func(function, expression, frame, vars_dict)

    args_string = ', '.join([str(a) if function.__name__ != '__str__' else '@@@@ self @@@@' for a in args])
    kwargs_string = ', '.join(f"{t[0]}={t[1]}" for t in kwargs.items())

    # Create an extra with the args and keywords.
    extra = f'args = {args_string}, kwargs = {kwargs_string}'

    # Create a Record key.
    record_key = Archive.Record.RecordKey(container_id, function.__name__, __FC__.__name__)

    # Create Record value.
    # First put a null value and update it after the function has been called with the value / exception.
    record_value = Archive.Record.RecordValue(record_key, func_type, None, expression, line_no, extra=extra)

    # Store with a "None" value, to make sure that the __FC__ will be recorded before the function has been called.
    if archive.should_record:
        archive.store(record_key, record_value)

    # Call the function.
    ret_exc = None
    try:
        ret_value = function(*args, **kwargs)
    except BaseException as e:
        ret_exc = e
        ret_value = ret_exc

    ret_value_to_store = POID(ret_value) if ret_exc is not None else ret_exc
    if archive.should_record:
        # Update the value of the called function (or exception).
        # record_value.value = ret_value
        record_value.value = ret_value_to_store

    if ret_exc:
        raise ret_exc
    # Return ret value.
    return ret_value


def __BMFCS__(func_stub_wrapper, caller: object, caller_str: str, func_name: str, line_no: int, arg: object, frame,
              locals, globals):
    if IS_BUILTIN_MANIPULATION_FUNCTION_CALL(caller):
        rv = archive.store_new \
            .key(id(caller), func_name, __BMFCS__.__name__, Archive.Record.StoreKind.BUILTIN_MANIP) \
            .value(type(caller), POID(arg), caller_str, line_no)

        # Store args that are temporary objects.
        # E.g.: l.add(Animal(...))
        if not ISP(type(arg)) and not id(arg) in {**locals, **globals}.values():
            __store(frame, '', line_no, id(arg), arg, rv.time, Archive.Record.StoreKind.UNAMED_OBJECT)


def __AC__(obj: object, attr: str, expr: str, locals: dict, globals: dict, line_no: int):
    # Access field (or method).
    field = obj.__getattribute__(attr) if type(obj) is not type else obj.__getattribute__(obj, attr)

    archive.store_new \
        .key(id(obj), attr, __AC__.__name__) \
        .value(type(field), POID(field), expr, line_no)

    return field


def __SOLI__(line_no: int, frame):
    if archive.should_record:
        archive.store_new \
            .key(id(frame), '__start_of_loop_iteration', __SOLI__.__name__) \
            .value(int, line_no, '__start_of_loop_iteration', line_no)


def __EOLI__(frame, loop_start_line_no: int, loop_end_line_no: int):
    if archive.should_record:
        archive.store_new \
            .key(id(frame), '__end_of_loop_iteration', __EOLI__.__name__) \
            .value(int, loop_start_line_no, '__end_of_loop_iteration', loop_end_line_no)


def __BREAK__(line_no: int, frame):
    if archive.should_record:
        archive.store_new \
            .key(id(frame), 'break', __BREAK__.__name__) \
            .value(object, None, 'break', line_no)


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


all_stubs = [__FLI__, __AS__]


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


def __PAUSE__():
    archive.pause_record()


def __RESUME__():
    archive.resume_record()


def __PRINT__(line_no: int, frame, *print_args):

    with StringIO() as capturer, redirect_stdout(capturer):
        print(*print_args)
        output = capturer.getvalue().strip('\n')

    if archive.should_record:
        archive.store_new \
            .key(id(frame), 'print', __PRINT__.__name__, Archive.Record.StoreKind.EVENT) \
            .value(type(print), f'{output}', f'print({", ".join([str(arg) for arg in print_args])}', line_no)

    print(output)


_T = TypeVar("_T")

__STUBS__ = [__AC__, __AS__, __RESUME__, __PAUSE__, __FRAME__, __ARG__,
             __FLI__, __DEF__, __PIS__, __POST_CONDITION__, __UNDEF__]


def __IS_STUBBED__(line: str) -> bool:
    return any([stub.__name__ in line for stub in __STUBS__])


# noinspection PyPep8Naming
class __PALADIN_LIST__(object):
    def __init__(self, elements: [] = None):
        if elements is None:
            self._inner = []
        else:
            self._inner = elements

    def append(self, __object: _T) -> None:
        self._inner = self._inner + [__object]
