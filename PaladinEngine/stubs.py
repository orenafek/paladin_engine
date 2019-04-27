import ast


def __FLI__(target):
    """
        A stub for a for loop.
    :param target: The target of the loop.
    :return:
    """
    print('Stub! target is {}'.format(target))


def __AS__(*targets, value) -> None:
    """
        A stub for assignment statement.
    :param targets: (list[ast.Name]) The targets being assigned.
    :param value: (ast.AST) The assigned value.
    :return: None
    """

    # Create the targets str:
    trgts_str = ', '.join([str(target) for target in targets])
    print('Assignment: {} = {}'.format(trgts_str, value))


def create_ast_stub(stub, *args, **kwargs):
    """
        Create an AST node from a stub.
    :param stub: (function) A stub
    :return:
    """

    # Initialize args list.
    arg_list = []

    for arg in args:
        if type(arg) is tuple:
            arg_name = arg[0]
            arg_type = arg[1]

            if arg_type is str:
                arg = "'{}'".format(arg_name)

        arg_list.append(arg)

    # Create the args list str.
    args_str = ', '.join([arg.strip() for arg in arg_list])

    # Create the kwargs list str.
    kwargs_str = ','.join('{}={}'.format(kw[0].strip(), kw[1].strip()) for kw in kwargs.items())

    # Create the args/kwargs list str.
    args_kwargs_str = ','.join([args_str, kwargs_str])

    # Create the call as a str.
    call_str = '{func}({args_kwargs})'.format(func=stub.__name__, args_kwargs=args_kwargs_str)

    # parse it.
    ast_node = ast.parse(call_str).body[0]

    return ast_node
