from dataclasses import dataclass


@dataclass
class Expr:
    pass


@dataclass
class Num(Expr):
    val: int


@dataclass
class Var(Expr):
    name: str


@dataclass
class Add(Expr):
    x: Expr
    y: Expr


@dataclass
class Mul(Expr):
    x: Expr
    y: Expr


class BaseVisitor:
    def visit(self, tree):
        meth = 'visit_' + type(tree).__name__
        return getattr(self, meth)(tree)


class FormatVisitor(BaseVisitor):
    def visit_Num(self, tree):
        return str(tree.val)

    def visit_Var(self, tree):
        return tree.name

    def visit_Add(self, tree):
        x = self.visit(tree.x)
        y = self.visit(tree.y)
        return f'({x} + {y})'

    def visit_Mul(self, tree):
        x = self.visit(tree.x)
        y = self.visit(tree.y)
        return f'({x} * {y})'


class SimplifyVisitor(BaseVisitor):
    def visit_Num(self, tree):
        return tree

    def visit_Var(self, tree):
        return tree

    def visit_Add(self, tree):
        x = self.visit(tree.x)
        y = self.visit(tree.y)
        if isinstance(x, Num) and isinstance(y, Num):
            return Num(x.val + y.val)
        elif isinstance(x, Num) and x.val == 0:
            return y
        elif isinstance(y, Num) and y.val == 0:
            return x
        return Add(x, y)

    def visit_Mul(self, tree):
        x = self.visit(tree.x)
        y = self.visit(tree.y)
        if isinstance(x, Num) and isinstance(y, Num):
            return Num(x.val * y.val)
        elif isinstance(x, Num) and x.val == 0:
            return Num(0)
        elif isinstance(y, Num) and y.val == 0:
            return Num(0)
        return Mul(x, y)


tree1 = Add(Mul(Var('x'), Num(2)), Mul(Var('y'), Num(4)))
tree2 = Add(Mul(Num(0), Var('x')), Add(Var('y'), Num(0)))
print(FormatVisitor().visit(tree1))
print(FormatVisitor().visit(SimplifyVisitor().visit(tree2)))
