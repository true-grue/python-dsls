import ast

OPS = {
    ast.Add: 'f64.add',
    ast.Sub: 'f64.sub',
    ast.Mult: 'f64.mul',
    ast.Div: 'f64.div',
    ast.Eq: 'f64.eq',
    ast.NotEq: 'f64.ne',
    ast.Lt: 'f64.lt',
    ast.LtE: 'f64.le',
    ast.Gt: 'f64.gt',
    ast.GtE: 'f64.ge',
    ast.USub: 'f64.neg'
}


def compile_expr(env, expr):
    match expr:
        case ast.Constant(float() | int() as value):
            return f'f64.const {value}'
        case ast.Name(name) if env[name] in ('param', 'local'):
            return f'local.get ${name}'
        case ast.BinOp(left, op, right) | ast.Compare(left, [op], [right]):
            left = compile_expr(env, left)
            right = compile_expr(env, right)
            return f'{left}\n{right}\n{OPS[type(op)]}'
        case ast.UnaryOp(op, left):
            return f'{compile_expr(env, left)}\n{OPS[type(op)]}'
        case ast.Call(ast.Name(name), args) if env[name] == 'func':
            args = '\n'.join(compile_expr(env, arg) for arg in args)
            return f'{args}\ncall ${name}'
        case ast.List([]):
            return f'call $list'
        case ast.Subscript(name, slice=slice):
            name = compile_expr(env, name)
            slice = compile_expr(env, slice)
            return f'{name}\n{slice}\ncall $get'


def compile_stmt(env, stmt):
    match stmt:
        case ast.Assign([ast.Name(name)], expr):
            if name not in env:
                env[name] = 'local'
            expr = compile_expr(env, expr)
            return f'{expr}\nlocal.set ${name}'
        case ast.Assign([ast.Subscript(name, slice=slice)], expr):
            name = compile_expr(env, name)
            slice = compile_expr(env, slice)
            expr = compile_expr(env, expr)
            return f'{name}\n{slice}\n{expr}\ncall $set'
        case ast.AugAssign(target=target, op=op, value=value):
            assign = ast.Assign([target], ast.BinOp(target, op, value))
            return compile_stmt(env, assign)
        case ast.If(test, true, false):
            test = compile_expr(env, test)
            true = compile_block(env, true)
            false = compile_block(env, false)
            return f'{test}\n(if\n(then\n{true}\n)\n(else\n{false}\n)\n)'
        case ast.While(test, body, []):
            test = compile_expr(env, test)
            body = compile_block(env, body)
            return (f'(block\n(loop\n{test}\ni32.eqz\nbr_if 1\n'
                    f'{body}\nbr 0\n)\n)')
        case ast.Return(value):
            env['$result'] = '(result f64)'
            return f'{compile_expr(env, value)}\nreturn'
        case ast.Expr(ast.Call(ast.Attribute(name, 'append'), [value])):
            name = compile_expr(env, name)
            value = compile_expr(env, value)
            return f'{name}\n{value}\ncall $append'
        case ast.Expr(ast.Call() as call):
            return compile_expr(env, call)


def compile_block(env, block):
    return '\n'.join([compile_stmt(env, stmt) for stmt in block])


def compile_func(env, name, args, body):
    env.update((arg.arg, 'param') for arg in args)
    body = compile_block(env, body)
    params = '\n'.join([f'(param ${arg.arg} f64)' for arg in args])
    locs = '\n'.join([f'(local ${name} f64)' for name in env
                     if env[name] == 'local'])
    return (f'(func ${name} (export "{name}")\n'
            f'{params}\n{env.get("$result", "")}\n{locs}\n{body}\n)')


def compile_module(imports, tree):
    env = {name: 'func' for name in imports}
    funcs = []
    for stmt in tree:
        match stmt:
            case ast.FunctionDef(name, args, body):
                env[name] = 'func'
                funcs.append(compile_func(env.copy(), name, args.args, body))
    imports = '\n'.join(imports.values())
    return f'(module\n{imports}\n%s\n)' % '\n'.join(funcs)


def add_import(imports, name, args, result):
    args = ' '.join(['(param f64)'] * args)
    res = '(result f64)' * result
    imports[name] = f'(import "lib" "{name}" (func ${name} {args} {res}))'


def pywasm(imports, src):
    add_import(imports, 'list', 0, 1)
    add_import(imports, 'append', 2, 0)
    add_import(imports, 'get', 2, 1)
    add_import(imports, 'set', 3, 0)
    return compile_module(imports, ast.parse(src).body)
