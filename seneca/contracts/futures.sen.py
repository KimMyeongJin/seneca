from seneca.libs.datatypes import hmap, table, hlist
from seneca.contracts.tau import get_current_price

asks = hlist('asks', table(None, {
    'seller': str, # VK of the seller issuing these contracts
    'volume': int, # Amount of commodity the seller wants to trade
    'price': float, # price per commodity count
    'delivery_date': float
}))
bids = hlist('bids', table(None, {
    'buyer': str,
    'price': float,
    'amount': int
}))

@export
def bid(price, amount):
    bids.append({
        'buyer': rt.sender,
        'price': price,
        'amount': amount
    })

@export
def ask(price, volume, delivery_date):
    assert price > 0, 'Price must be greater than 0'
    assert volume > 0, 'Volume must be greater than 0'
    asks.append({
        'seller': rt.sender,
        'price': price,
        'volume': volume,
        'delivery_date': delivery_date
    })

@export
def settle():
    price = get_current_price()
