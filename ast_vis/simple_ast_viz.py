import ast
import inspect


DOT_STYLE = ('node [fontname= "JetBrains Mono" fontsize=20\n'
             'style=filled fillcolor="#E5FDCD" penwidth=2]')


def to_dot(graph, labels):
    dot = []
    dot.append(f'digraph G {{\n{DOT_STYLE}')
    for n in graph:
        dot.append(f'{n} [label="{labels[n]}" shape=box]')
    for a in graph:
        for b in graph[a]:
            dot.append(f'{a} -> {b}')
    dot.append('}')
    return '\n'.join(dot)


def ast_viz(tree):
    graph, labels = {}, {}

    def make_node(tree):
        node_id = len(graph)
        graph[node_id] = []
        labels[node_id] = type(tree).__name__
        return node_id

    def walk(parent_id, tree):
        match tree:
            case ast.AST():
                node_id = make_node(tree)
                graph[parent_id].append(node_id)
                for field in tree._fields:
                    walk(node_id, getattr(tree, field))
            case list():
                for elem in tree:
                    walk(parent_id, elem)

    walk(make_node(tree), tree.body)
    return to_dot(graph, labels)


def foo(x):
    return x * 2


tree = ast.parse(inspect.getsource(foo))
print(ast_viz(tree))
