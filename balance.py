# Example for get balance of accounts in python
from kucoin.client import Market
from kucoin.client import User

'''
If you want to use this bot, edit parameters to yourself in this Python File and in main.py
'''


def get_valid_currencies():
    client = User("YOUR API_KEY", "YOUR API_SECRET", "YOUR API_PASSPHRASE")  # EDIT THIS!
    symbols = client.get_account_list()
    result_symbols = {}
    for symbol in symbols:
        if symbol['type'] == 'trade':
            result_symbols.update([(f"{symbol['currency']}-USDT", symbol['balance'])])
    client = Market("YOUR API_KEY", "YOUR API_SECRET", "YOUR API_PASSPHRASE")  # EDIT THIS!
    market_symbols = client.get_symbol_list()
    result_valid_symbols = {}
    for market_symbol in market_symbols:
        if market_symbol['symbol'] in result_symbols:
            if float(market_symbol['baseMinSize']) <= float(result_symbols[market_symbol['symbol']]):
                result_valid_symbols.update([(market_symbol['symbol'].replace('-USDT', ''),
                                              result_symbols[market_symbol['symbol']])])
    return result_valid_symbols


if __name__ == '__main__':
    get_valid_currencies()
