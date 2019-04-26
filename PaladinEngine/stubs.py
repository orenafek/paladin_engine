import ast


def for_loop_stub(target):
    """
        A stub for a for loop.
    :param target: The target of the loop.
    :return:
    """
    print('Stub! target is {}'.format(target))


def assignment_stub(*targets, value) -> None:
    """
        A stub for assignment statement.
    :param targets: (list[ast.Name]) The targets being assigned.
    :param value: (ast.AST) The assigned value.
    :return: None
    """

    # Create the targets str:
    trgts_str = ', '.join([target for target in targets])
    print('Assignment: {} = {}'.format(trgts_str, value))


def create_ast_stub(stub, *args, **kwargs):
    """
        Create an AST node from a stub.
    :param stub: (function) A stub
    :return:
    """
    # Create the args list str.
    args_str = ', '.join([arg for arg in args])

    # Create the kwargs list str.
    kwargs_str = ','.join('{}={}'.format(kw[0], kw[1]) for kw in kwargs.items())

    # Create the args/kwargs list str.
    args_kwargs_str = ','.join([args_str, kwargs_str])

    # Create the call as a str.
    call_str = '{func}({args_kwargs})'.format(func=stub.__name__, args_kwargs=args_kwargs_str)

    # parse it.
    ast_node = ast.parse(call_str).body[0]

    return ast_node
