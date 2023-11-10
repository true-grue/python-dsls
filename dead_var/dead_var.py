import ast
import inspect
from datalog import datalog
from cfg import walk_cfg


def get_du(node, defs, uses):
    match node:
        case ast.Name(name, ast.Load()):
            uses.append(name)
        case ast.Name(name, ast.Store()) | ast.arg(name):
            defs.append(name)
        case ast.AST():
            for field in node._fields:
                defs, uses = get_du(getattr(node, field), defs, uses)
        case list():
            for elem in node:
                defs, uses = get_du(elem, defs, uses)
    return defs, uses


@datalog
def dead_var():
    live_in(P, V) <= used(P, V)
    live_in(P, V) <= ~defined(P, V), live_out(P, V)
    live_out(P1, V) <= edge(P1, P2), live_in(P2, V)
    dead_var(P, V) <= defined(P, V), ~live_out(P, V)


class CFGAnalysis:
    def __init__(self):
        self.dlog = dead_var()

    def node(self, node):
        if node not in ('start', 'end'):
            defs, uses = get_du(node, [], [])
            for d in defs:
                self.dlog.add_fact('defined', node, d)
            for u in uses:
                self.dlog.add_fact('used', node, u)

    def edge(self, src, dst):
        self.dlog.add_fact('edge', src, dst)

    def get_dead_vars(self):
        _, dead_vars = self.dlog.query('dead_var(Node, Var)')
        return [(row['Var'], row['Node']) for row in dead_vars]


def foo(a, b, c):
    x = 0
    if a:
        a = 0
        x = 1
    else:
        x = 2
    a = 1
    b = 2
    return x


src = inspect.getsource(foo)

g = CFGAnalysis()
walk_cfg(g, ast.parse(src))
for var, node in g.get_dead_vars():
    if 'lineno' in node._attributes:
        print(f'Dead assignment to {repr(var)}, line {node.lineno}')
    else:
        print(repr(var))
