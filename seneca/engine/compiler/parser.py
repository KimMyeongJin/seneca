from seneca.engine.compiler.transformer import NodeTransformer
from seneca.engine.interpreter.scope import Export, Seed, Function
from seneca.constants.whitelists import SAFE_BUILTINS
from seneca.libs.math.decimal import to_decimal
from seneca.libs.metering.resource import set_resource_limits
import ast, copy
from pprint import pprint


def parse_ast(code_str):
    tree = ast.parse(code_str)
    t = NodeTransformer()
    tree = t.visit(tree)
    ast.fix_missing_locations(tree)
    return {
        'tree': tree,
        'exports': t.exports,
        'imports': t.imports,
        'methods': t.methods,
        'contract_vars': t.contract_vars
    }


def get_contract_scope_from_meta(contract_meta):
    scope = {
        'export': Export(),
        'seed': Seed(),
        '__set_resources__': set_resource_limits,
        '__decimal__': to_decimal,
        '__function__': Function(),
        '__builtins__': SAFE_BUILTINS
    }
    keys_before_exec = list(scope.keys())
    # print('BEFORE EXEC')
    # pprint(scope)
    instantialized_scope = {}
    code_obj = compile(contract_meta['tree'], '__main__', 'exec')
    exec(code_obj, scope)
    keys_after_exec = list(scope.keys())
    # print('AFTER EXEC')
    # pprint(scope)
    assert len(keys_after_exec) > len(keys_before_exec), 'No objects had been added after running the contract'
    for var, value in contract_meta['contract_vars'].items():
        instantialized_scope[var] = scope.get(value)
        del scope[var]
        del scope[value]
    for func_name in contract_meta['methods']:
        instantialized_scope[func_name] = scope.get(func_name)
        del scope[func_name]
    for module, alias in contract_meta['imports']:
        del scope[alias or module]
    keys_after_cleanup = list(scope.keys())
    assert keys_after_cleanup == keys_before_exec, 'Not properly cleaned up'
    # print('AFTER CLEANUP')
    # pprint(scope)
    return instantialized_scope

