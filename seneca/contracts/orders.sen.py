from seneca.libs.datatypes import hmap, hlist, ranked, table
from seneca.contracts.currency import balance_of, transfer

bids = ranked('bids')
asks = ranked('asks')
bid_orders = hmap('bid_orders', str, table(None, {
    'order_status': str,
    'user': str,
    'price': str,
    'amount': float
}))
ask_orders = hmap('ask_orders', str, table(None, {
    'order_status': str,
    'user': str,
    'price': str,
    'amount': float
}))

@export
def bid(bid_price, amount):
    assert balance_of(rt.sender) >= bid_price * amount, 'Not enough funds to bid'
    ask_order_id = asks.get_min()
    ask_price = ask_orders[ask_order_id]['price']
    if bid_price >= ask_price:
        order_status = 'filled'
        ask_orders[bid_order_id]['order_status'] = order_status
    else:
        order_status = 'pending'
    bids.increment('order_id', 1)
    bid_order_id = bids.score('order_id')
    bid_orders[bid_order_id] = {
        'order_status': order_status,
        'buyer': rt.sender,
        'price': price,
        'amount': amount
    }
    print('Placed a bid', bid_orders[bid_order_id])

@export
def ask(ask_price, amount):
    bid_order_id = bids.get_max()
    bid_price = bid_orders[bid_order_id]['price']
    if bid_price >= bid_price:
        order_status = 'filled'
        bid_orders[bid_order_id]['order_status'] = order_status
    else:
        order_status = 'pending'
    asks.increment('order_id', 1)
    ask_order_id = asks.score('order_id')
    ask_orders[ask_order_id] = {
        'order_status': order_status,
        'buyer': rt.sender,
        'price': price,
        'amount': amount
    }
    print('Placed an ask', bid_orders[bid_order_id])
