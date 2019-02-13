from seneca.libs.datatypes import hmap, table
from seneca.libs.crypto.hashing import hash_data
from seneca.libs.importing import import_contract

swaps = hmap('swaps', str, hmap(key_type=bytes, value_type=table(schema={
	'initiator': str,
	'participant': str,
	'amount': int,
	'token': str,
	'expiration': int,
})))

def initiate(initiator,
	participant,
	expiration,
	hashlock,
	token,
	amount):

	if not swaps[participant][hashlock]:

		token_contract = import_contract(token)
		assert token_contract.allowance(rt['origin'], participant) >= amount, 'Not enough allowance to initiate swap.'
		token_contract.transfer_from(rt['contract'], amount)

		swaps[participant][hashlock] = {
			'initiator': initiator,
			'participant': participant,
			'amount': amount,
			'token': token,
			'expiration': expiration
		}

def redeem(secret):
	digest = hash_data(secret, 'sha3_256')
	if swaps[rt['origin']][digest]:
		s = swaps[rt['origin']][digest]
		assert s['participant'] == rt['origin'], 'Not authorized to redeem'

		token = import_contract(s['token'])
		token.transfer(rt['origin'], s['amount'])

def refund(participant, secret):
	digest = hash_data(secret, 'sha3_256')
	assert swaps[participant][digest], 'Swap not found'
	s = swaps[participant][digest]
	# TODO figure out time
	# assert s['expiration'] < now, 'The swap is expired.'
	assert s['initiator'] == rt['origin'], 'Cannot refund. You are not the initiator.'
	token = import_contract(s['token'])
	print(token.balance_of(rt['origin']))
	print(token.balance_of(participant))
	token.transfer(rt['origin'], s['amount'])
	print(token.balance_of(rt['origin']))
	print(token.balance_of(participant))
