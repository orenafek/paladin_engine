import ast


def ast2str(node: ast.AST, lstrip: bool = True, rstrip: bool = True) -> str:
    unparsed = ast.unparse(node)

    if not lstrip and not rstrip:
        return unparsed

    if lstrip and not rstrip:
        stripper = str.lstrip
    elif rstrip and not lstrip:
        stripper = str.rstrip
    else:
        stripper = str.strip

    return stripper(unparsed)


def str2ast(s: str):
    return ast.parse(s).body[0]


def wrap(s: str, w: str, wrap_left: bool = True, wrap_right: bool = True) -> str:
    return w + s + w if wrap_left and wrap_right \
        else w + s \
        if wrap_right == '' \
        else s + w \
        if wrap_left == '' \
        else s

def wrap_str_param(s: str):
    # TODO: Patch for passing strings with strings inside, their ' and " are replaced with @
    s = s.replace('"','@').replace("'", '@')
    return wrap(s, '\'') if not '\'' in s else wrap(s, '"')