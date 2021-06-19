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
