from __future__ import annotations
from typing import NamedTuple, assert_never


class Num(NamedTuple):
    val: int


class Var(NamedTuple):
    name: str


class Add(NamedTuple):
    x: Expr
    y: Expr


class Mul(NamedTuple):
    x: Expr
    y: Expr


Expr = Num | Var | Add | Mul


def compile_expr(tree: Expr) -> str:
    match tree:
        case Num(val) | Var(val):
            return f'PUSH {repr(val)}'
        case Add(a, b):
            x = compile_expr(a)
            y = compile_expr(b)
            return f'{x}\n{y}\nADD'
        case Mul(a, b):
            x = compile_expr(a)
            y = compile_expr(b)
            return f'{x}\n{y}\nMUL'
        case _ as unreachable:
            assert_never(unreachable)


tree = Add(Mul(Var('x'), Num(2)), Mul(Var('y'), Num(4)))
print(compile_expr(tree))
