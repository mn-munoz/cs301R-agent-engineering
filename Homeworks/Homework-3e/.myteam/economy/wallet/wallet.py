wallet = 80

transactions = [
    {"description": "Purchased loadout: Health Potion and Moonberry Rations", "amount": -20}
]

def get_wallet_balance():
    return wallet

def add_to_wallet(amount):
    global wallet
    wallet += amount
    return wallet

def subtract_from_wallet(amount):
    global wallet
    if amount > wallet:
        raise ValueError("Insufficient funds in wallet.")
    wallet -= amount
    return wallet

def record_transaction(description, amount):
    transactions.append({"description": description, "amount": amount})

def get_transaction_history():
    return transactions
