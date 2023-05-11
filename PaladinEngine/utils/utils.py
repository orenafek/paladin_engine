from typing import Tuple

from archive.archive_evaluator.archive_evaluator_types.archive_evaluator_types import Identifier, LineNo
from archive.archive_evaluator.paladin_dsl_config.paladin_dsl_config import SCOPE_SIGN


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


def separate_line_no(obj: Identifier) -> Tuple[Identifier, LineNo]:
    if isinstance(obj, str) and SCOPE_SIGN in obj:
        split = obj.split(SCOPE_SIGN)
        return split[0], int(split[1])
    else:
        return obj, -1
