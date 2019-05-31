import ast

from archive.archive import Archive

archive = Archive()


def __FLI__(locals, globals):
    """
        A stub for a for loop.
    :param locals: The local names accessible from the loop.
    :param locals: The global names accessible from the loop.
    :return:
    """
    all_vars = {**locals, **globals}

    n = all_vars['n']

    result = all_vars['result']

    if abs(n) >= 1:
        assert result >= all([v for v in archive.values('result')])
    else:
        assert result < all([v for v in archive.values('result')])


def __AS__(*assignment_pairs) -> None:
    """
        A stub for assignment statement.
    :param assignment_pairs: (list[(str, str]) A list of pairs of assignment pairs of:
                                               (target, value)
    :return: None
    """

    # Iterate over the targets of the assignment.
    for assignment_pair in assignment_pairs:
        # Record the value.
        archive[assignment_pair[0]] = assignment_pair[1]


def create_ast_stub(stub, *args, **kwargs):
    """
        Create an AST node from a stub.
    :param stub: (function) A stub
    :return:
    """

    # Initialize args list.
    arg_list = []

    for arg_tuple_list in args:

        # Initialize the inner tuple string.
        inner_tuple_strings = []
        for arg_tuple in arg_tuple_list:

            # Extract the argument's name.
            arg_name = arg_tuple[0]

            # Extract the argument's type.
            arg_type = arg_tuple[1]

            if arg_type is StubArgumentType.PLAIN:
                arg = "{}".format(arg_name)
            elif arg_type is StubArgumentType.NAME:
                arg = "'{}'".format(arg_name)
            else:
                raise NotImplementedError('arg_type is not of of type: ', StubArgumentType)

            # Add to the inner tuple strings list.
            inner_tuple_strings.append(arg)

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
