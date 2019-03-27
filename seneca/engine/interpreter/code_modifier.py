import ast

class CodeModifier(ast.NodeTransformer):
    def __init__(self, suffix):
        self.var_names = []
        self.check_already_modified = True
        self.cleanup_decorator = "@cleanup"
        self.suffix_r = suffix

    def visit_FunctionDef(self, node):
        return node

    def visit_AsyncFunctionDef(self, node):
        return node

    def visit_ClassDef(self, node):
        return node

    def visit_Assign(self, node):
        for t in node.targets:
            self.var_names.append(t.id)
        return node

    def visit_AugAssign(self, node):
        self.var_names.append(node.target.id)
        return  node

    def visit_AnnAssign(self, node):
        self.var_names.append(node.target.id)
        return  node

    def visit_Global(self, node):
        for n in node.names:
            self.var_names.append(n)
        return  node

    def get_unique_substr(self, code_str, prefix):
        while prefix in code_str:
            prefix = prefix + self.suffix_r
        return prefix

    def add_reset_method(self, code_str, var_names):
        if not var_names:
            return code_str
        func_name = self.get_unique_substr(code_str, '_cleanup')
        self.check_already_modified = True
        self.cleanup_decorator = "# @cleanup"
        code_str += "\n" + self.cleanup_decorator + "\ndef " + func_name + "():\n"
        for vname in var_names:
            code_str += "    " + vname + " = None\n"
        return code_str

    def transform(self, code_str, prefix):
        # return code_str
        if self.check_already_modified and self.cleanup_decorator in code_str:
            return code_str
        self.var_names.clear()
        tree = ast.parse(code_str)
        self.visit(tree)
        # not needed as there is no issue of recursive prefixing
        # trname = self.get_unique_substr(code_str, '_zxq_')
        # prefix = self.get_unique_substr(code_str, prefix)
        mod_var_names = []
        for vname in self.var_names:
            rname = f'{prefix}_{vname}'
            rname = self.get_unique_substr(code_str, rname)
            # code_str = code_str.replace(vname, trname)
            # code_str = code_str.replace(trname, rname)
            code_str = code_str.replace(vname, rname)
            mod_var_names.append(rname)
        # print(self.var_names)
        # print(code_str)
        # print(mod_var_names)
        code_str = self.add_reset_method(code_str, mod_var_names)
        return code_str

