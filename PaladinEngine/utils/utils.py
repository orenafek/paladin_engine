

def assert_not_raise(f, *args, **kwargs):
    try:
        if args == () and kwargs == {}:
            f()
        elif args != () and kwargs == {}:
            f(*args)
        elif args == () and kwargs != {}:
            f(**kwargs)
        else:
            f(*args, **kwargs)

    except BaseException as e:
        raise AssertionError(f'Invocation of {f} has failed because {e}.')