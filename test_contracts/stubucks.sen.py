from seneca.libs.storage.datatypes import Hash
from seneca.contracts.currency import mint

balances = Hash('balances', default_value=0)
custodials = Hash('custodials', default_value=0)

@seed
def seed():
    balances['435e3264395e24eb37a0eb6c322421e701dc332db45536d25eac67924b9321aa'] = 1000000
    # print('seeding', balances.key, '435e3264395e24eb37a0eb6c322421e701dc332db45536d25eac67924b9321aa',
    #       balances['435e3264395e24eb37a0eb6c322421e701dc332db45536d25eac67924b9321aa'])

@export
def transfer(to, amount):
    assert balances[rt['sender']] >= amount, 'oh nooo i blew up'
    balances[to] += amount
    balances[rt['sender']] -= amount

@export
def add_to_custodial(to, amount):
    assert balances[rt['sender']] >= amount
    custodials[rt['sender']][to] += amount
    balances[rt['sender']] -= amount

@export
def remove_from_custodial(to, amount):
    assert custodials[rt['sender']][to] >= amount
    balances[rt['sender']] += amount
    custodials[rt['sender']][to] -= amount

@export
def spend_custodial(_from, amount, to):
    assert custodials[_from][rt['sender']] >= amount, 'Not enough funds to transfer from "{}" to "{}"'.format(_from, rt['sender'])

    balances[to] += amount
    custodials[_from][rt['sender']] -= amount

@export
def get_balance(account):
    return balances[account]

@export
def get_custodial(owner, spender):
    return custodials[owner][spender]

@export
def mint(to, amount):
    # print('xxx: minting', balances.key, to, balances[to])
    # print("multiply-minting {} to wallet {} (originally {})".format(amount, to, balances[to]))
    balances[to] *= amount
    # print(balances[to], amount)
