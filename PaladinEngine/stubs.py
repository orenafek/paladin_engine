import ast
import inspect

from PaladinEngine.archive.archive import Archive
from interactive_debugger import InteractiveDebugger

archive = Archive()
from Examples.Tetris.tetris import Board, Block


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
        if abs(n) >= 1:
            assert result >= all(archive.retrieve('result'))
        else:
            assert result < all(archive.retrieve('result'))
    except BaseException:
        InteractiveDebugger(archive, f'For Loop invariant: {error_line}\nhas been broken.', 21).cmdloop()


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


def __AS__(*assignment_pairs, locals, globals, frame, line_no) -> None:
    """
        A stub for assignment statement.
    :param assignment_pairs: (list[(str, str]) A list of pairs of assignment pairs of:
                                               (target, value)
    :return: None
    """

    # Iterate over the targets of the assignment.
    for assignment_triplet in assignment_pairs:
        # Record the value.
        try:
            if len(assignment_triplet) > 2:
                object_and_value_to_store = assignment_triplet[0:2]
                sl = assignment_triplet[2::]
            else:
                object_and_value_to_store = assignment_triplet
                sl = None

            archive.store(*object_and_value_to_store, frame=frame, vars_dict={**locals, **globals}, line_no=line_no,
                          slice=sl)

        except BaseException as e:
            print(e)


def create_ast_stub(stub, *args, **kwargs):
    """
        Create an AST node from a stub.
    :param stub: (function) A stub
    :return:
    """

    def convert_arg_tuple_to_str(arg_tuple):
        # Extract the argument's name.
        arg_name = arg_tuple[0]

        # Extract the argument's type.
        arg_type = arg_tuple[1]

        if arg_type is StubArgumentType.PLAIN:
            arg_str = f"{arg_name}"
        elif arg_type is StubArgumentType.NAME:
            arg_str = f"'{arg_name}'"
        elif arg_type is StubArgumentType.ID:
            arg_str = f"id({arg_name})"

        else:
            raise NotImplementedError('arg_type is not of of type: ', StubArgumentType)

        return arg_str

    # Initialize args list.
    arg_list = []

    for arg_tuple_list in args:
        # Initialize the inner tuple string.
        inner_tuple_strings = []
        for arg_tuple in arg_tuple_list:
            if type(arg_tuple) in [list, tuple] and any([type(arg) in [list, tuple] for arg in arg_tuple]):
                # Add to the inner tuple strings list.
                inner_tuple_strings.extend([convert_arg_tuple_to_str(arg) for arg in arg_tuple])
            else:
                inner_tuple_strings.append(convert_arg_tuple_to_str(arg_tuple))

        arg_list.append('({})'.format(', '.join(inner_tuple_strings)))

    # Create the args list str.
    args_str = ', '.join([arg.strip() for arg in arg_list])

    # Create the kwargs list str.
    kwargs_str = ','.join('{}={}'.format(kw[0].strip(), kw[1].strip()) for kw in kwargs.items())

    # Create the args/kwargs list str.
    if args_str == '':
        args_kwargs_str = kwargs_str
    elif kwargs_str == '':
        args_kwargs_str = args_str
    else:
        args_kwargs_str = ','.join([args_str, kwargs_str])

    # Create the call as a str.
    call_str = '{func}({args_kwargs})'.format(func=stub.__name__, args_kwargs=args_kwargs_str)

    # parse it.
    ast_node = ast.parse(call_str).body[0]

    return ast_node


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
