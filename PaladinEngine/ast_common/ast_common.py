import ast
from dataclasses import dataclass, field
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


def is_tuple(s: str) -> bool:
    return len(split_tuple(s)) > 1


def split_tuple(s: str) -> List[str]:
    node = ast.parse(s).body[0]
    if not isinstance(node, ast.Expr):
        return []

    if not isinstance(node.value, ast.Tuple):
        return [ast2str(node)]

    return list(map(lambda e: ast2str(e), node.value.elts))


def get_arg_from_func_call(func_call: str, func: Callable, arg_name: str) -> Optional[str]:
    if func.__name__ not in func_call or arg_name not in func.__code__.co_varnames:
        return None

    arg_var_pos = func.__code__.co_varnames.index(arg_name)

    try:
        node: ast.AST = str2ast(func_call.strip())
        if isinstance(node, ast.Expr):
            ast_call = cast(ast.Call, node.value)
        elif isinstance(node, ast.Raise):
            ast_call = cast(ast.Call, node.exc)
        else:
            raise RuntimeError()
        return ast2str(ast_call.args[arg_var_pos])
    except AttributeError:
        return None


def separate_to_container_and_field(expression: str, frame, locals: dict, globals: dict) -> tuple[
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

def split_attr(expression: str):
    return expression.split(".")