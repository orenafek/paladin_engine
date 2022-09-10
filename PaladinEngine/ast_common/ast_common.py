import ast
from typing import *

LiteralTypes = [int, float, str, bool, complex]
AnyLiteralType = NewType('AnyLiteralType', Union[int, float, str, bool, complex])


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


def is_of(s: str, t: Type) -> bool:
    parsed = str2ast(s)
    return type(parsed) is ast.Expr and isinstance(parsed.value, t)


def lit2ast(v: AnyLiteralType) -> Union[ast.Constant, ast.Name, ast.NameConstant]:
    if type(v) in [int, float, complex, complex]:
        return ast.Constant(value=v)

    if type(v) is str:
        return ast.Name(id=v)


def wrap(s: str, w: str, wrap_left: bool = True, wrap_right: bool = True) -> str:
    return w + s + w if wrap_left and wrap_right \
        else w + s \
        if wrap_right == '' \
        else s + w \
        if wrap_left == '' \
        else s


def wrap_str_param(s: str):
    # TODO: Patch for passing strings with strings inside, their ' and " are replaced with @
    # s = s.replace('"','@').replace("'", '@')
    s = s.replace('"', '\"').replace("'", "\'")
    return wrap(s, '\'') if not '\'' in s else wrap(s, '"')


def find_closest_parent(n: ast.AST, c: ast.AST, t: type):
    """
        Find closest parent of n from an indirect (or direct) container c of n of type t
    :param n:
    :param c:
    :param t:
    :return:
    """

    class ChildrenVisitor(ast.NodeVisitor):
        def __init__(self):
            self.closest_parent = c

        def visit(self, node: ast.AST):
            for child in ast.iter_child_nodes(node):
                if child == n:
                    self.closest_parent = node if isinstance(node, t) else self.closest_parent

            return self.generic_visit(node)

    cv = ChildrenVisitor()
    cv.visit(c)
    return cv.closest_parent
