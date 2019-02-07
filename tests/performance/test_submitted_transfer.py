from unittest import TestCase
from seneca.engine.interface import SenecaInterface
from seneca.engine.interpreter import SenecaInterpreter, ReadOnlyException
from seneca.constants.config import get_redis_port, MASTER_DB, DB_OFFSET, get_redis_password
from os.path import join
from tests.utils import captured_output
import redis, unittest, seneca, time
r = redis.StrictRedis(host='localhost', port=get_redis_port(), db=MASTER_DB, password=get_redis_password())

test_contracts_path = seneca.__path__[0] + '/../test_contracts/'
CONTRACT_COUNT = 10000
SENDER = '324ee2e3544a8853a3c5a0ef0946b929aa488cbe7e7ee31a0fef9585ce398502'

class TestPublishTransfer(TestCase):

    def setUp(self):
        r.flushdb()
        self.si = SenecaInterface(concurrent_mode=False, bypass_currency=True)
        self.author = SENDER
        self.sender = SENDER
        self.rt = {'rt': {'sender': self.sender, 'author': self.author, 'contract': 'test'}}
        print('''
################################################################################
{}
################################################################################
        '''.format(self.id))
        self.publish_contract()
        self.mint_account()
        self.code_str = '''
from seneca.contracts.currency import transfer
transfer('ass', 1)
        '''
        self.print_balance()
        self.code_obj = self.si.compile_code(self.code_str)
        self.start = time.time()

    def tearDown(self):
        elapsed = time.time() - self.start
        print('Finished {} contracts in {}s!'.format(CONTRACT_COUNT, elapsed))
        print('Rate: {}tps'.format(CONTRACT_COUNT / elapsed))
        self.print_balance()

    def publish_contract(self):
        with open(join(test_contracts_path, 'currency.sen.py')) as f:
            self.si.publish_code_str('currency', 'falcon', f.read())

    def mint_account(self):
        self.si.execute_code_str("""
from seneca.contracts.currency import mint
mint('{}', {})
        """.format(SENDER, CONTRACT_COUNT), self.rt)

    def print_balance(self):
        self.si.execute_code_str("""
from seneca.contracts.currency import balance_of
print('stu has a balance of: ' + str(balance_of('{}')))
print('ass has a balance of: ' + str(balance_of('ass')))
        """.format(SENDER), self.rt)

    def test_transfer_template_with_metering(self):
        for i in range(CONTRACT_COUNT):
            self.si.execute_function('test_contracts.currency.transfer',
                self.sender, 100000, 'ass', amount=1)

if __name__ == '__main__':
    unittest.main()
