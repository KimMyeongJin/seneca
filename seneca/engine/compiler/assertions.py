from seneca.constants.whitelists import ALLOWED_AST_TYPES, ALLOWED_IMPORT_PATHS, SENECA_LIBRARY_PATH, ALLOWED_DATA_TYPES
import ast


class ReadOnlyException(Exception):
    pass


class CompilationException(Exception):
    pass


class Assert:

    @staticmethod
    def is_valid_ast_types(n):
        if type(n) not in ALLOWED_AST_TYPES:
            raise CompilationException('Illegal AST type: {}'.format(n))

    @staticmethod
    def is_not_system_variable(name):
        if name[0] == '_':
            raise CompilationException('Access denied for system variable: {}'.format(name))

    @staticmethod
    def is_valid_import_path(name):
        if Check.is_smart_contract(name) or Check.is_module_lib(name):
            return
        raise CompilationException('Access denied for system variable: {}'.format(name))

    @staticmethod
    def no_nested_imports(node):
        for item in node.body:
            if type(item) in [ast.ImportFrom, ast.Import]:
                raise CompilationException('Not allowed to import inside a function definition')

    @staticmethod
    def is_datatype(node, t):
        if type(node.value) == ast.Tuple:
            raise CompilationException('You may not unpack multiple values')
        elif type(node.value) == ast.Call and type(t) == ast.Name and node.value.func.id in ALLOWED_DATA_TYPES:
            return
        raise CompilationException('You may only assign DataType variables in the global scope')



class Check:
    @staticmethod
    def is_smart_contract(name):
        for allowed_path in ALLOWED_IMPORT_PATHS:
            if allowed_path in name:
                return True

    @staticmethod
    def is_module_lib(name):
        if name.rsplit('.', 2)[0] in SENECA_LIBRARY_PATH:
            return True
