from seneca.contracts.orders import bid, ask
from seneca.contracts.currency import mint, balance_of

mint(rt.sender, 3000)
print(
    balance_of(rt.sender)
)
bid(2.00, 1000)
ask(2.10, 500)
