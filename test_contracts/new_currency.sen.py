from seneca.libs.storage.map import Map
from seneca.libs.storage.resource import Resource
from seneca.libs.storage.table import Table

# Declare Data Types
xrate = Resource()
seed_amount = Resource()
balances = Map('balances')
# allowed = hmap('allowed', str, hmap(key_type=str, value_type=int))

@seed
def initalize_currency():

    # Initialization
    xrate = 1.0
    seed_amount = 1000000
    # balances['LamdenReserves'] = 0

    # # Deposit to all network founders
    # founder_wallets = [
    #     '324ee2e3544a8853a3c5a0ef0946b929aa488cbe7e7ee31a0fef9585ce398502',
    #     'a103715914a7aae8dd8fddba945ab63a169dfe6e37f79b4a58bcf85bfd681694',
    #     '20da05fdba92449732b3871cc542a058075446fedb41430ee882e99f9091cc4d',
    #     'ed19061921c593a9d16875ca660b57aa5e45c811c8cf7af0cfcbd23faa52cbcd',
    #     'cb9bfd4b57b243248796e9eb90bc4f0053d78f06ce68573e0fdca422f54bb0d2',
    #     'c1f845ad8967b93092d59e4ef56aef3eba49c33079119b9c856a5354e9ccdf84'
    # ]
    #
    # for w in founder_wallets:
    #     balances[w] = seed_amount
