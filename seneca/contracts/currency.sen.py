from seneca.libs.datatypes import hmap

balances = hmap('balances', str, int)
allowed = hmap('allowed', str, hmap(value_type=int))
locks = hmap('locks', str, int)

@export
def balance_of(wallet_id):
    return balances[wallet_id]

@export
def transfer(to, amount):
    assert balances[rt.sender] >= amount, "Sender does not have enough funds for transfer"

    balances[rt.sender] -= amount
    balances[to] += amount

@export
def approve(spender, amount):
    allowed[rt.sender][spender] = amount

@export
def transfer_from(_from, to, amount):
    assert allowed[_from][rt.sender] >= amount
    assert balances[_from] >= amount

    allowed[_from][rt.sender] -= amount
    balances[_from] -= amount
    balances[to] += amount

@export
def allowance(approver, spender):
    return allowed[approver][spender]

@export
def mint(to, amount):
    assert rt.sender == rt.author, 'Only the original contract author can mint!'
    balances[to] += amount

@export
def lock(lockname, amount, expiration=0):
    assert balances[rt.sender] >= amount, "Sender does not have enough funds for transfer"
    balances[rt.sender] -= amount
    balances[rt.caller+lockname] += amount
    # locks[rt.caller+lockname] = rt.current_time + expiration

@export
def unlock(lockname):
    # assert rt.current_time >= locks[rt.caller+lockname], 'Cannot unlock funds as the lock is still active'
    balances[rt.sender] += amount
    balances[rt.caller+lockname] -= amount
