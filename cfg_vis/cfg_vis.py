import ast
import inspect
from cfg import walk_cfg


DOT_STYLE = ('node [fontname= "JetBrains Mono" fontsize=20\n'
             'style=filled fillcolor="#FDEDCD" penwidth=2]')


class CFGViz:
    def __init__(self):
        self.dot = [f'digraph G {{\n{DOT_STYLE}']

    def node(self, node):
        label = node if node in ('start', 'end') else ast.unparse(node)
        self.dot.append(f'{id(node)} [label="{label}" shape=box]')

    def edge(self, src, dst):
        self.dot.append(f'{id(src)} -> {id(dst)}')

    def to_dot(self):
        return '\n'.join(self.dot + ['}'])


def fact(x):
    y = 1
    while x > 1:
        y *= x
        x -= 1
    return y


src = inspect.getsource(fact)

g = CFGViz()
walk_cfg(g, ast.parse(src))
print(g.to_dot())
