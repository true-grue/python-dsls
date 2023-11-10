import ast
import inspect
import z3

BV_SIZE = 32


class Datalog:
    def __init__(self):
        self.fp = z3.Fixedpoint()
        self.fp.set(engine='datalog')
        self.vars = {}
        self.bounded = []
        self.val_to_idx = {}
        self.idx_to_val = {}
        self.relations = {}

    def get_var(self, name):
        if name not in self.vars:
            self.vars[name] = z3.Const(name, z3.BitVecSort(BV_SIZE))
            self.fp.declare_var(self.vars[name])
        self.bounded.append(self.vars[name])
        return self.vars[name]

    def get_value(self, value):
        if value not in self.val_to_idx:
            self.val_to_idx[value] = len(self.val_to_idx)
            self.idx_to_val[self.val_to_idx[value]] = value
        return z3.BitVecVal(self.val_to_idx[value], BV_SIZE)

    def get_relation(self, name, arity):
        if name not in self.relations:
            args = [z3.BitVecSort(BV_SIZE)] * arity
            self.relations[name] = z3.Function(name, *args, z3.BoolSort())
            self.fp.register_relation(self.relations[name])
        return self.relations[name]

    def compile_term(self, term):
        match term:
            case ast.Name(name) if name[0].isupper():
                return self.get_var(name)
            case ast.Name(value) | ast.Constant(value):
                return self.get_value(value)

    def compile_atom(self, atom):
        match atom:
            case ast.Call(ast.Name(name), args):
                relation = self.get_relation(name, len(args))
                return relation(*(self.compile_term(arg) for arg in args))
            case ast.UnaryOp(ast.Invert(), atom):
                return z3.Not(self.compile_atom(atom))

    def compile_stmt(self, rule):
        self.bounded = []
        match rule:
            case ast.Expr(ast.Tuple([ast.Compare(head,
                                                 [ast.LtE()], first), *rest])):
                body = z3.And(*(self.compile_atom(x) for x in first + rest))
                return self.compile_atom(head), body
            case ast.Expr(ast.Compare(head, [ast.LtE()], [first])):
                return self.compile_atom(head), self.compile_atom(first)
            case ast.Expr(atom):
                return self.compile_atom(atom), None

    def parse_cols(self, names, answer):
        match answer.decl().name():
            case '=':
                name = names[z3.get_var_index(answer.arg(0))]
                return {name: self.idx_to_val[answer.arg(1).as_long()]}
            case 'and':
                row = {}
                for x in answer.children():
                    row.update(self.parse_cols(names, x))
                return row

    def parse_rows(self, names, answer):
        match answer.decl().name():
            case '=' | 'and':
                return [self.parse_cols(names, answer)]
            case 'or':
                return [self.parse_cols(names, x) for x in answer.children()]
            case _:
                return []

    def query(self, query):
        head, _ = self.compile_stmt(ast.parse(query).body[0])
        if not self.bounded:
            return self.fp.query(head), []
        q = z3.Exists(self.bounded, head)
        names = {i: q.var_name(i) for i in range(q.num_vars())}
        return self.fp.query(q), self.parse_rows(names, self.fp.get_answer())

    def add_fact(self, name, *args):
        relation = self.get_relation(name, len(args))
        self.fp.add_rule(relation(*(self.get_value(arg) for arg in args)))


def datalog(f):
    d = Datalog()
    tree = ast.parse(inspect.getsource(f))
    for rule in tree.body[0].body:
        d.fp.add_rule(*d.compile_stmt(rule))
    return lambda: d
