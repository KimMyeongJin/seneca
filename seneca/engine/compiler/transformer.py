from seneca.engine.compiler.assertions import Assert, Check
import ast


class NodeTransformer(ast.NodeTransformer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contract_vars = {}
        self.methods = {}
        self.exports = {}
        self.imports = []
        self.scope = 'global'

    def generic_visit(self, node):
        Assert.is_valid_ast_types(node)
        return super().generic_visit(node)

    def visit_ImportFrom(self, node):
        for n in node.names:
            Assert.is_valid_import_path(node.module)
            if Check.is_smart_contract(node.module):
                if type(n) == ast.alias:
                    self.imports.append((n.name, n.asname))

        self.generic_visit(node)
        return node

    def visit_Assign(self, node):
        if self.scope == 'global':
            for t in node.targets:
                Assert.is_datatype(node, t)
                self.contract_vars[t.id] = node.value.func.id
                self.generic_visit(node)
                node.value.args = [ast.Str(t.id)] + node.value.args
                return node
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        Assert.no_nested_imports(node)
        old_scope = self.scope
        self.scope = 'func'
        for d in node.decorator_list:
            if d.id in ('export', 'seed'):
                self.scope = d.id
            if d.id == 'export':
                self.exports[node.name] = {
                    'func_type': self.scope,
                    'args': self._get_args(node)
                }
        self.methods[node.name] = {
            'func_type': self.scope,
            'args': self._get_args(node)
        }
        self.generic_visit(node)
        node.decorator_list.append(
            ast.Name(id='__function__', ctx=ast.Load())
        )
        self.scope = old_scope
        return node

    def _get_args(self, node):
        arguments = []
        for arg in node.args.args:
            annotation = arg.annotation.id if arg.annotation else None
            # defaults = node.args.defaults  #TODO consider defaults
            arguments.append({
                'arg_name': arg.arg,
                'arg_type': annotation
            })
        return arguments

    def visit_Num(self, node):
        # NOTE: Integers are important for indexing and slicing so we cannot replace them. They also will not suffer
        #       from rounding issues.
        if isinstance(node.n, float):  # or isinstance(node.n, int):
            return ast.Call(func=ast.Name(id='__decimal__', ctx=ast.Load()),
                            args=[node], keywords=[])
        self.generic_visit(node)
        return node
