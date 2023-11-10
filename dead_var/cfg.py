import ast


def add_node(graph, node):
    graph.node(node)
    return node, [node]


def connect(graph, outs, node):
    for out in outs:
        graph.edge(out, node)


def walk_if(graph, test, true, false):
    start_in, start_outs = add_node(graph, test)
    true_in, all_outs = walk_block(graph, true)
    connect(graph, start_outs, true_in)
    if false:
        false_in, false_outs = walk_block(graph, false)
        connect(graph, start_outs, false_in)
        all_outs += false_outs
    else:
        all_outs += start_outs
    return start_in, all_outs


def walk_while(graph, test, body):
    test_in, test_outs = add_node(graph, test)
    body_in, body_outs = walk_block(graph, body)
    connect(graph, test_outs, body_in)
    connect(graph, body_outs, test_in)
    return test_in, test_outs


def walk_stmt(graph, stmt):
    match stmt:
        case ast.If(test, true, false):
            return walk_if(graph, test, true, false)
        case ast.While(test, body):
            return walk_while(graph, test, body)
        case ast.Return():
            return_in, return_outs = add_node(graph, stmt)
            connect(graph, return_outs, 'end')
            return return_in, []
        case _:
            return add_node(graph, stmt)


def walk_block(graph, block):
    first, *rest = block
    start_in, start_outs = walk_stmt(graph, first)
    end_in, end_outs = start_in, start_outs
    for stmt in rest:
        prev_in, prev_outs = end_in, end_outs
        end_in, end_outs = walk_stmt(graph, stmt)
        connect(graph, prev_outs, end_in)
    return start_in, end_outs


def walk_cfg(graph, tree):
    for stmt in tree.body:
        match stmt:
            case ast.FunctionDef(name, args, body):
                _, start_outs = add_node(graph, 'start')
                end_in, _ = add_node(graph, 'end')
                body_in, body_outs = walk_block(graph, body)
                for arg in args.args:
                    args_in, args_outs = add_node(graph, arg)
                    connect(graph, start_outs, args_in)
                    connect(graph, args_outs, body_in)
                if not args.args:
                    connect(graph, start_outs, body_in)                    
                connect(graph, body_outs, end_in)
