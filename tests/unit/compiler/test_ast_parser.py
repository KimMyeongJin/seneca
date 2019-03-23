from tests.utils import TestCaseHeader
from seneca.engine.interpreter.executor import Executor
from seneca.engine.compiler.parser import parse_ast, get_contract_scope_from_meta
from pprint import pprint


class TestAstParser(TestCaseHeader):

    def setUp(self):
        super().__init__()
        self.ex = Executor(concurrency=False, metering=False)
        self.ex.driver.flushall()
        self.magic = '''
@export
def magical_move():
    print('this is magic')
    
def secret_move():
    print('this is secret magic')
        '''
        self.melee = '''
@export
def physical_move():
    print('this is melee')
    
def secret_move():
    print('this is secret melee')
        '''
        self.magician = '''
from seneca.contracts import Magic
from seneca.contracts import Melee as Strength
from seneca.libs.storage.datatypes import Hash, Resource

moves = Hash()
tools = Resource()

@seed
def initialize_magician():
    moves['slight_of_hands'] = True

@export
def learn_move(move_name: str, move_pp=20):
    moves[move_name] = True

def make_move(move_name):
    assert moves[move_name], 'You dont have this move'
    print('You just made the {} move'.format(move_name))
        '''

    def _get_contract_scope(self, code_str):
        meta = parse_ast(code_str)
        return get_contract_scope_from_meta(meta)

    def test_parse_full_contract(self):
        magic = self._get_contract_scope(self.magic)
        melee = self._get_contract_scope(self.melee)
        self.ex.publish_contract('Magic', self.magic)
        self.ex.publish_contract('Melee', self.melee)
        magician = self._get_contract_scope(self.magician)
        # print(magician)

        # contract_scope['Magic'].magical_move()
        # contract_scope['Magic'].secret_move()
        # contract_scope['Strength'].magical_move()
        # contract_scope['Strength'].secret_move()
        # pprint(code_objs)
