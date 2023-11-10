import ast

DOT_STYLE = ('node [fontname= "JetBrains Mono" fontsize=20\n'
             'style=filled fillcolor="#FDEDCD" penwidth=2]')


def get_error_details(src, node, filename=''):
    return (filename,
            node.lineno,
            node.col_offset + 1,
            ast.get_source_segment(src, node),
            node.end_lineno,
            node.end_col_offset + 1)


def all_instances_of(lst, cls):
    return all(isinstance(node, cls) for node in lst)


def add_edges(dot, prev, ops, names):
    for op, name in zip(ops, names):
        match op:
            case ast.Gt():
                dot.append(f'{prev} -> {name.id}')
            case ast.Lt():
                dot.append(f'{name.id} -> {prev}')
        prev = name.id


def graph_viz(src):
    dot = [f'digraph G {{\n{DOT_STYLE}']
    for stmt in ast.parse(src).body:
        match stmt:
            case ast.Expr(ast.Compare(ast.Name(prev), ops, names)) \
                    if all_instances_of(ops, (ast.Gt, ast.Lt)) \
                    and all_instances_of(names, ast.Name):
                add_edges(dot, prev, ops, names)
            case ast.AnnAssign(ast.Name(x), ast.Constant(str(y))):
                dot.append(f'{x} [label="{y}"]')
            case _:
                raise SyntaxError('bad graph syntax',
                                  get_error_details(src, stmt))
    return '\n'.join(dot + ['}'])


src = '''
n1 > n2 > n4 > n8
n1 > n3 > n6 > n12
n2 > n5 > n10
n3 > n7 > n14
n4 > n9
n5 > n11
n6 > n13
n7 > n15
n1: 'root'
'''

print(graph_viz(src))
