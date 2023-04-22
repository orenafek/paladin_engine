import abc
import ast
import re
import sys
from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from types import NoneType
from typing import Optional, Union, TypeVar, Tuple, List, Dict, Set, Callable, Any

from archive.archive import Archive
from ast_common.ast_common import str2ast, ast2str
from builtin_manipulation_calls.builtin_manipulation_calls import BuiltinCollectionsUtils, EMPTY, EMPTY_COLLECTION
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


def __AC__(obj: object, attr: str, expr: str, locals: dict, globals: dict, line_no: int):
    # Access field (or method).
    field = obj.__getattribute__(attr) if type(obj) is not type else obj.__getattribute__(obj, attr)

    archive.store_new \
        .key(id(obj), attr, __AC__.__name__) \
        .value(type(field), POID(field), expr, line_no)

    return field


def __ARG__(func_name: str, arg: str, value: object, locals: dict, globals: dict, frame,
            line_no: int):
    archive.store_new \
        .key(id(frame), arg, __ARG__.__name__) \
        .value(type(value), POID(value), arg, line_no)

    if func_name == '__init__' and arg == 'self':
        # FIXME: Handling only cases when __init__ is called as __init__(self [,...]),
        # FIXME: Meaning that if __init__ is called with a firs arg which is not "self", this wouldn't work.
        archive.store_new \
            .key(id(frame), PALADIN_OBJECT_COLLECTION_FIELD, __AS__.__name__) \
            .value(type(value), value, PALADIN_OBJECT_COLLECTION_EXPRESSION, line_no)


def __AS__(expression: str, target: str, locals: dict, globals: dict, frame, line_no: int) -> None:
    if not archive.should_record:
        return

    container_id, field, container, is_container_value, is_container_id_frame = _separate_to_container_and_field(target,
                                                                                                                 frame,
                                                                                                                 locals,
                                                                                                                 globals)
    value = container if is_container_value else container.__getattribute__(
        field) if field in container.__dict__ else None

    __store(container_id, field, line_no, target, value, locals, globals, __AS__,
            kind=Archive.Record.StoreKind.VAR if is_container_id_frame else Archive.Record.StoreKind.OBJ_ITEM)


# The first param "func_stub_wrapper" is not used but passed to this stub to be evaluated before entering here.
# noinspection PyUnusedLocal
def __BMFCS__(func_stub_wrapper, caller: object, caller_str: str, func_name: str, line_no: int, frame,
              locals, globals, arg: Optional[object] = EMPTY):
    if BuiltinCollectionsUtils.is_builtin_collection_method(caller):
        rv = archive.store_new \
            .key(id(caller), func_name, __BMFCS__.__name__, Archive.Record.StoreKind.BUILTIN_MANIP) \
            .value(type(caller), (type(arg), (POID(arg) if arg != EMPTY else EMPTY)), caller_str, line_no)

        # Store args that are temporary objects.
        # E.g.: l.add(Animal(...))
        if not ISP(type(arg)) and not id(arg) in [id(x) for x in {**locals, **globals}.values()] and arg != EMPTY:
            __store(frame, '', line_no, id(arg), arg, locals, globals, __BMFCS__, rv.time,
                    Archive.Record.StoreKind.UNAMED_OBJECT)


def __BREAK__(line_no: int, frame):
    if archive.should_record:
        archive.store_new \
            .key(id(frame), 'break', __BREAK__.__name__) \
            .value(object, None, 'break', line_no)


def __DEF__(func_name: str, line_no: int, frame):
    archive.store_new \
        .key(id(frame), func_name, __DEF__.__name__) \
        .value(type(lambda _: _), func_name, func_name, line_no)


def __EOLI__(frame, loop_start_line_no: int, loop_end_line_no: int):
    archive.store_new \
        .key(id(frame), '__end_of_loop_iteration', __EOLI__.__name__) \
        .value(int, loop_start_line_no, '__end_of_loop_iteration', loop_end_line_no)


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

    # Call the function.
    ret_exc = None
    try:
        ret_value = function(*args, **kwargs)
    except BaseException as e:
        ret_exc = e
        ret_value = ret_exc

    vars_dict = {**locals, **globals}

    # Find container.
    container_id = _separate_to_container_and_func(function, expression, frame, vars_dict)

    # args_string = ', '.join([str(a) if function.__name__ != '__str__' else '@@@@ self @@@@' for a in args])
    # kwargs_string = ', '.join(f"{t[0]}={t[1]}" for t in kwargs.items())

    # Create an extra with the args and keywords.
    # extra = f'args = {args_string}, kwargs = {kwargs_string}'
    extra = ''

    if archive.should_record:
        # Store with a "None" value, to make sure that the __FC__ will be recorded before the function has been called.
        __store(container_id, function.__name__, line_no, function.__name__, ret_value, locals, globals, __FC__,
                kind=Archive.Record.StoreKind.FUNCTION_CALL,
                extra=extra)

    if ret_exc:
        raise ret_exc
    # Return ret value.
    return ret_value


def __FLI__(locals, globals):
    raise NotImplementedError()


def __FRAME__():
    return sys._getframe(1)


def __IS_STUBBED__(line: str) -> bool:
    return any([stub.__name__ in line for stub in __STUBS__])


def __PAUSE__():
    archive.pause_record()


def __PIS__(first_param: object, first_param_name: str, line_no: int):
    # TODO: Should type(first_param) be int instead?
    archive.store_new \
        .key(Archive.GLOBAL_PALADIN_CONTAINER_ID, first_param_name, __PIS__.__name__) \
        .value(type(first_param), id(first_param), first_param_name, line_no)


def __PRINT__(line_no: int, frame, *print_args):
    with StringIO() as capturer, redirect_stdout(capturer):
        print(*print_args)
        output = capturer.getvalue().strip('\n')

    if archive.should_record:
        archive.store_new \
            .key(id(frame), 'print', __PRINT__.__name__, Archive.Record.StoreKind.EVENT) \
            .value(type(print), f'{output}', f'print({", ".join([str(arg) for arg in print_args])}', line_no)

    print(output)


def __RESUME__():
    archive.resume_record()


def __SOL__(frame, loop_start_line_no: int):
    archive.store_new \
        .key(id(frame), '__start_of_loop', __SOL__.__name__) \
        .value(int, loop_start_line_no, '__start_of_loop', loop_start_line_no)


def __SOLI__(line_no: int, frame):
    if archive.should_record:
        archive.store_new \
            .key(id(frame), '__start_of_loop_iteration', __SOLI__.__name__) \
            .value(int, line_no, '__start_of_loop_iteration', line_no)


def __UNDEF__(func_name: str, line_no: int, frame):
    archive.store_new \
        .key(id(frame), func_name, __UNDEF__.__name__) \
        .value(type(lambda _: _), func_name, func_name, line_no)


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
    int, str, object, bool, bool]:
    expression_ast = str2ast(expression).value
    if isinstance(expression_ast, ast.Subscript):
        getitem_arg = f'''{slice.__name__}(start={ast2str(expression_ast.slice.lower)},
                                           stop={ast2str(expression_ast.slice.upper)},
                                           step={ast2str(expression_ast.slice.step)})
                       ''' if isinstance(expression_ast.slice, ast.Slice) else eval(ast2str(expression_ast.slice),
                                                                                    globals, locals)
        subscript_value = eval(ast2str(expression_ast.value), globals, locals)
        return id(subscript_value), getitem_arg, eval(expression, globals, locals), True, False

    if not isinstance(expression_ast, ast.Attribute):
        # There is only an object.
        value = eval(expression, globals, locals)
        return id(frame), expression, value, True, True

    container = eval(ast2str(expression_ast.value), globals, locals)
    field = expression_ast.attr if type(expression_ast.attr) is str else ast2str(expression_ast.attr)

    return id(container), field, container, False, False


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


_T = TypeVar("_T")

__STUBS__ = [__AC__, __ARG__, __AS__, __BMFCS__, __BREAK__, __DEF__, __EOLI__, __FC__, __FLI__, __FRAME__,
             __IS_STUBBED__, __PAUSE__, __PIS__, __PRINT__, __RESUME__, __SOL__, __SOLI__, __UNDEF__]


# noinspection PyPep8Naming
class __PALADIN_LIST__(object):
    def __init__(self, elements: [] = None):
        if elements is None:
            self._inner = []
        else:
            self._inner = elements

    def append(self, __object: _T) -> None:
        self._inner = self._inner + [__object]


def __store(container_id, field, line_no, target, value, locals, globals,
            stub: Callable = __AS__,
            _time: Optional[int] = None, kind: Archive.Record.StoreKind = Archive.Record.StoreKind.VAR,
            extra: Any = None):
    stored_objects = set()

    value_to_store = POID(value)
    rv = archive.store_new \
        .key(container_id, field, stub.__name__, kind) \
        .value(type(value), value_to_store, str(target), line_no, extra=extra)

    if _time:
        rv.time = _time

    def _store_inner(v: object) -> None:
        if id(v) in stored_objects:
            return None

        stored_objects.add(id(v))

        if ISP(type(v)) or v is None or issubclass(type(v), type):
            return None

        if type(v) in [list, tuple, set]:
            return _store_lists_tuples_and_sets(v)

        if issubclass(type(v), dict):
            return _store_dicts(id(v), v)

        if not hasattr(v, '__dict__'):
            return None

        return _store_dicts(id(v), v.__dict__)

    def _store_lists_tuples_and_sets(v: Union[List, Tuple, Set]):

        if len(v) == 0 and v is not None:
            # Empty collection.
            archive.store_new \
                .key(id(v), '', __AS__.__name__, Archive.Record.StoreKind.kind_by_type(type(v))) \
                .value(NoneType, EMPTY_COLLECTION, '', line_no, time=rv.time)
            return

        for index, item in enumerate(v):
            archive.store_new \
                .key(id(v), index, __AS__.__name__, Archive.Record.StoreKind.kind_by_type(type(v))) \
                .value(type(item), POID(item), f'{type(v)}[{index}]', line_no, time=rv.time)

            _store_inner(item)

    def _store_dicts(d_id: int, d: Dict):
        for k, v in d.items():
            archive.store_new \
                .key(d_id, POID(k), __AS__.__name__, Archive.Record.StoreKind.DICT_ITEM) \
                .value((type(k), type(v)), POID(v), f'{id(d)}[{POID(k)}] = {POID(v)}', line_no, time=rv.time)

            _store_inner(k)
            _store_inner(v)

    if not ISP(type(value)) and not id(value) in {id(x) for x in stored_objects}:
        _store_inner(value)
