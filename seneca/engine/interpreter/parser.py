from seneca.engine.interpreter.scope import Export, Seed, Function
from seneca.constants.whitelists import SAFE_BUILTINS
from seneca.engine.interpreter.utils import Plugins, Assert
from seneca.libs.math.decimal import to_decimal
from seneca.libs.metering.resource import set_resource_limits
from collections import defaultdict
import ast, copy
from seneca.constants.config import *


class Parser:
    basic_scope = {
        'export': Export(),
        'seed': Seed(),
        '__set_resources__': set_resource_limits,
        '__decimal__': to_decimal,
        '__function__': Function(),
        '__builtins__': SAFE_BUILTINS
    }
    parser_scope = {
        'ast': None,
        'callstack': [],
        'namespace': defaultdict(dict),
        'exports': defaultdict(dict),
        'imports': {},
        'resources': {},
        'methods': defaultdict(dict),
        'protected': defaultdict(set)
    }
    seed_tree = None
    child = None
    initialized = False
    assigning = False

    @classmethod
    def reset(cls):
        # cls.initialize()
        cls.parser_scope.update({
            'imports': {},
            '__args__': (),
            '__kwargs__': {}
        })
        cls.parser_scope.update(cls.basic_scope)
        cls.parser_scope['protected']['__global__'].update(cls.basic_scope.keys())
        cls.parser_scope['protected']['__global__'].update(('rt',))
        cls.seed_tree = None
        cls.assigning = None
        cls.parser_scope['ast'] = None

    @staticmethod
    def parse_ast(code_str):
        # Parse tree
        tree = ast.parse(code_str)
        Parser.seed_tree = copy.deepcopy(tree)
        Parser.seed_tree.body = []
        tree = NodeTransformer().visit(tree)
        ast.fix_missing_locations(tree)

        return Parser.seed_tree


class NodeTransformer(ast.NodeTransformer):

    @property
    def contract_name(self):
        return Parser.parser_scope['rt']['contract']

    @property
    def resource(self):
        return Parser.parser_scope['resources']

    def get_resource(self, name):
        contract_name = Parser.parser_scope['imports'].get(name, self.contract_name)
        resource_name = '{}{}{}'.format(contract_name, CONTRACT_NAME_DELIM, name)
        while True:
            resource = Parser.parser_scope['resources'].get(resource_name)
            if resource:
                if resource[0] == POINTER:
                    contract_name = resource[1:]
                    resource_name = '{}{}{}'.format(contract_name, CONTRACT_NAME_DELIM, name)
                else:
                    return resource, contract_name
            else:
                return None, None

    def set_resource(self, resource, func_name, contract_name=None):
        contract_name = contract_name or self.contract_name
        resource_name = '{}{}{}'.format(contract_name, CONTRACT_NAME_DELIM, resource)
        Parser.parser_scope['resources'][resource_name] = func_name

    @property
    def protected(self):
        return Parser.parser_scope['protected'].get(self.contract_name, {})

    def generic_visit(self, node):
        Assert.ast_types(node)
        return super().generic_visit(node)

    def visit_Name(self, node):
        if Parser.assigning is not None and node.id in Parser.assigning:
            Assert.is_protected(node, Parser.parser_scope)
        if not Parser.parser_scope.get('__system__'):
            Assert.not_system_variable(node.id)
        Assert.is_within_scope(node.id, self.protected, self.resource, Parser.parser_scope)
        if Parser.assigning:
            Assert.is_not_resource(Parser.assigning, node.id, Parser.parser_scope)
        if Parser.parser_scope['ast'] in ('seed', 'export', 'func'):
            resource, contract_name = self.get_resource(node.id)
            if resource:
                if resource == 'Resource':
                    self.generic_visit(node)
                    node.id = '{}{}{}'.format(contract_name, CONTRACT_NAME_DELIM, node.id)
                    return Plugins.resource_reassignment(node.id, node.ctx)
                node.id = '{}{}{}'.format(contract_name, CONTRACT_NAME_DELIM, node.id)
        self.generic_visit(node)
        return node



    def visit_Attribute(self, node):
        Assert.not_system_variable(node.attr)
        self.generic_visit(node)
        return node

    def visit_Import(self, node):
        for i, n in enumerate(node.names):
            node.names[i] = self.validate_imports(n.name, alias=n.asname, node=n)
        return self._visit_any_import(node)

    def visit_ImportFrom(self, node):
        for i, n in enumerate(node.names):
            node.names[i] = self.validate_imports(node.module, n.name, alias=n.asname, node=n)
        return self._visit_any_import(node)

    def validate_imports(self, import_path, module_name=None, alias=None, node=None):
        contract_name = import_path.split('.')[-1]
        module_type = Assert.valid_import_path(import_path, module_name)
        if module_type == 'smart_contract':
            Parser.parser_scope['imports'][module_name] = contract_name
            self.set_resource(alias or module_name, '{}{}'.format(POINTER, contract_name))
            Parser.parser_scope['protected'][module_name].add(contract_name)
            node = self._prefix_resource_with_contract_name(node, import_path.split('.')[-1])
        elif module_type == 'lib_module':
            Parser.parser_scope['protected']['__global__'].add(module_name)
        return node

    def _prefix_resource_with_contract_name(self, node, contract_name):
        if type(node) == ast.alias:
            node.name = '{}{}{}'.format(contract_name, CONTRACT_NAME_DELIM, node.name)
            # print(node.name)
        elif type(node) == ast.Name:
            node.id = '{}{}{}'.format(contract_name, CONTRACT_NAME_DELIM, node.id)
            # print(node.id)
        elif type(node) == ast.Attribute:
            node.value = self._prefix_resource_with_contract_name(node.value, contract_name)
            # print(node.value)
        else:
            # v = node.value
            # print('\n\n', self.contract_name, ':', dir(v))
            # print(v)
            pass

        return node

    def _visit_any_import(self, node):
        if Parser.parser_scope['ast'] == None:
            Parser.parser_scope['ast'] = 'import'
        Parser.seed_tree.body.append(node)
        self.generic_visit(node)
        Parser.parser_scope['ast'] = None
        return node

    def visit_Assign(self, node):
        resource_names, func_name = Assert.valid_assign(node, Parser.parser_scope)
        if resource_names and func_name:
            for resource in resource_names:
                resource_name = '{}{}{}'.format(self.contract_name, CONTRACT_NAME_DELIM, resource)
                node.value.args = [ast.Str(resource_name)]
                self.set_resource(resource, func_name)
            Parser.seed_tree.body.append(node)
            for i, t in enumerate(node.targets):
                node.targets[i] = self._prefix_resource_with_contract_name(t, self.contract_name)
        Parser.assigning = resource_names
        self.generic_visit(node)
        Parser.assigning = None
        return node

    def visit_AugAssign(self, node):
        Assert.is_protected(node.target, Parser.parser_scope)
        Parser.assigning = [node.target]
        self.generic_visit(node)
        Parser.assigning = None
        return node

    def visit_Call(self, node):
        print('compiling', Parser.parser_scope['rt']['contract'])
        if Parser.parser_scope['ast'] in ('seed', 'export', 'func'):
            Assert.not_datatype(node)
            if type(node.func) == ast.Name:
                contract_name = Parser.parser_scope['imports'].get(node.func.id)
                print('\t', Parser.parser_scope)
                print('\t', node.func.id, contract_name)
                if contract_name:
                    node.func.id = '{}{}{}'.format(contract_name, CONTRACT_NAME_DELIM, node.func.id)
                    # print(node.func.id)
                # else:
                #     print(node.func.id)
            # elif type(node.func) == ast.Attribute:
            #     if type(node.func.value) == ast.Name:
            #         contract_name = Parser.parser_scope['imports'].get(node.func.value.id)
            #         v = contract_name
            #         # print(dir(v))
            #         print('name', v)
                # print(Parser.parser_scope.get('exports'))
                # print(Parser.parser_scope.get('imports'))
            # node.func = self._prefix_resource_with_contract_name(node.func)
            # resource, contract_name = self.get_resource(node.func)
            # print(resource, contract_name)
            # v = node.func
            # print(dir(v))
            # print(v)
            self.generic_visit(node)
            return node
        if not Parser.parser_scope['ast']:
            Assert.is_datatype(node)
        self.generic_visit(node)
        return node

    def visit_Num(self, node):
        # NOTE: Integers are important for indexing and slicing so we cannot replace them. They also will not suffer
        #       from rounding issues.
        if isinstance(node.n, float):  # or isinstance(node.n, int):
            return ast.Call(func=ast.Name(id='__decimal__', ctx=ast.Load()),
                            args=[node], keywords=[])
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        original_ast_scope = Parser.parser_scope['ast']
        if original_ast_scope is None:
            Assert.no_nested_imports(node)
            ast_set = False
            for d in node.decorator_list:
                if d.id in ('export', 'seed'):
                    Parser.parser_scope['ast'] = d.id
                    ast_set = d.id
            if not ast_set:
                Parser.parser_scope['ast'] = 'func'
            if Parser.parser_scope['ast'] == 'export':
                Parser.parser_scope['exports'][self.contract_name][node.name] = True
            if Parser.parser_scope['ast'] in ('export', 'seed', 'func'):
                # print('\t>>>>', self.contract_name, node.name)
                self.generic_visit(node)
                # print('\t<<<<', self.contract_name, node.name)
            Parser.parser_scope['ast'] = original_ast_scope
        node.decorator_list.append(ast.Name(id='__function__', ctx=ast.Load()))
        node.name = '{}{}{}'.format(self.contract_name, CONTRACT_NAME_DELIM, node.name)
        Parser.seed_tree.body.append(node)
        return node
