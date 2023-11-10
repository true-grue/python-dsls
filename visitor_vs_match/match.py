from collections import namedtuple

Num = namedtuple('Num', 'val')
Var = namedtuple('Var', 'name')
Add = namedtuple('Add', 'x y')
Mul = namedtuple('Mul', 'x y')


def format_expr(tree):
    match tree:
        case Num(val) | Var(val):
            return str(val)
        case Add(x, y):
            x = format_expr(x)
            y = format_expr(y)
            return f'({x} + {y})'
        case Mul(x, y):
            x = format_expr(x)
            y = format_expr(y)
            return f'({x} * {y})'


def simplify(tree):
    match tree:
        case Add(Num(x), Num(y)):
            return Num(x + y)
        case Mul(Num(x), Num(y)):
            return Num(x * y)
        case Add(Num(0), x) | Add(x, Num(0)):
            return x
        case Mul(Num(0), x) | Mul(x, Num(0)):
            return Num(0)
    return tree


def simplify_expr(tree):
    result = tree
    match tree:
        case Num() | Var():
            result = tree
        case Add(x, y):
            result = Add(simplify_expr(x), simplify_expr(y))
        case Mul(x, y):
            result = Mul(simplify_expr(x), simplify_expr(y))
    return simplify(result)


tree1 = Add(Mul(Var('x'), Num(2)), Mul(Var('y'), Num(4)))
tree2 = Add(Mul(Num(0), Var('x')), Add(Var('y'), Num(0)))
print(format_expr(tree1))
print(format_expr(simplify_expr(tree2)))
