import sys
import time

from kucoin.client import Market

from kucoin.client import Trade

from balance import get_valid_currencies

from secretdata.secretdata import Data

'''
If you want to use this bot, edit parameters to yourself in this Python File and in balance.py
'''
client_market = Market(Data.api_key, Data.api_secret, Data.api_passphrase)  # EDIT THIS!
client_trade = Trade(Data.api_key, Data.api_secret, Data.api_passphrase)  # EDIT THIS!


def ask_user(balance):
    """
    :param balance: this data got from get_valid_currencies function that located from balance.py
    :return: user_input
    :type: str
    """
    user_input = input('How currency do you want to roll?(Enter name of valid currency)\n'
                       f'{", ".join(balance)}\n').upper()
    if user_input in balance.keys():
        return user_input + '-USDT'
    else:
        print('ERROR: Invalid currency')
        ask_user(balance)


def check_price(symbol_to_roll):
    """
    :param symbol_to_roll: symbol that we can roll (inputted from a user)
    :return: price of symbol
    :type: str
    """
    price = client_market.get_ticker(symbol_to_roll)['price']
    return price


def sell_template(symbol_to_roll, symbol_income_percent, symbol_stop):
    """
    Sell template for avoiding duplicates
    :param symbol_income_percent:
    :param symbol_stop:
    :param symbol_to_roll: symbol that we can roll (inputted from a user)
    :return: that's nothing to return, because it's template for another function
    """
    symbol_to_roll_balance = get_valid_currencies()[symbol_to_roll.replace('-USDT', '')]
    symbol_price = float(check_price(symbol_to_roll))
    symbol_decimal = str(symbol_price)[::-1].find('.')
    symbol_price_stop = round(symbol_price - symbol_price * symbol_stop, symbol_decimal)
    symbol_price_buy = round((symbol_price + symbol_price * symbol_income_percent), symbol_decimal)
    order_sell_id = client_trade.create_limit_order(symbol_to_roll, 'sell', symbol_to_roll_balance,
                                                    symbol_price_buy)['orderId']
    print(f"Stop is worked or {order_sell_id} is ordered of sale by"
          f" {round(symbol_price + symbol_price * 0.01, symbol_decimal)}")
    sell_currency(order_sell_id, symbol_to_roll, symbol_price_stop)


def buy_template(symbol_to_roll, symbol_income_percent, symbol_stop):
    """
    Buy template for avoiding duplicates
    :param symbol_stop:
    :param symbol_income_percent:
    :param symbol_to_roll: symbol that we can roll (inputted from a user)
    :return: that's nothing to return, because it's template for another function
    """
    symbol_to_roll_balance = get_valid_currencies()[symbol_to_roll.replace('-USDT', '')]
    symbol_price = float(check_price(symbol_to_roll))
    symbol_decimal = str(symbol_price)[::-1].find('.')
    symbol_price_stop = round(symbol_price + symbol_price * symbol_stop, symbol_decimal)
    symbol_price_sell = round((symbol_price - symbol_price * symbol_income_percent), symbol_decimal)
    order_buy_id = client_trade.create_limit_order(symbol_to_roll, 'buy', symbol_to_roll_balance,
                                                   symbol_price_sell)['orderId']
    print(f"Stop is worked or {order_buy_id} is ordered of purchase by"
          f" {round(symbol_price - symbol_price * symbol_income_percent, symbol_decimal)}")
    buy_currency(order_buy_id, symbol_to_roll, symbol_price_stop, symbol_income_percent, symbol_stop)


def buy_currency(order_id, symbol_to_roll, symbol_price_stop, symbol_income_percent, symbol_stop):
    """
        This function buys currency and check if stops/cancel is triggered
        :param symbol_stop:
        :param symbol_income_percent:
        :param symbol_price_stop: symbol price for re-create order
        :param order_id: Order ID was given by buy template
        :param symbol_to_roll: symbol that we can roll (inputted from a user)
        :return: that's function nothing to return
        """
    market_price = float(client_market.get_ticker(symbol_to_roll)['price'])
    try:
        while True:
            order_buy_id = client_trade.get_order_details(order_id)
            isOrderCancel = order_buy_id['cancelExist']
            isOrderActive = order_buy_id['isActive']
            if isOrderCancel is True:
                print('Order is cancelled!')
            else:
                if market_price <= symbol_price_stop:
                    buy_template(symbol_to_roll, symbol_income_percent, symbol_stop)
                if isOrderActive is False:
                    sell_template(symbol_to_roll, symbol_income_percent, symbol_stop)
            time.sleep(1.500)
    except Exception as e:
        sys.exit(e)


def sell_currency(order_id, symbol_to_roll, symbol_price_stop, symbol_income_percent, symbol_stop):
    """
    This function sells currency and check if stops/cancel is triggered
    :param symbol_stop:
    :param symbol_income_percent:
    :param symbol_price_stop: symbol price for re-create order
    :param order_id: Order ID was given by buy template
    :param symbol_to_roll: symbol that we can roll (inputted from a user)
    :return: that's function nothing to return
    """
    market_price = float(client_market.get_ticker(symbol_to_roll)['price'])
    try:
        while True:
            order_sell_id = client_trade.get_order_details(order_id)
            isOrderCancel = order_sell_id['cancelExist']
            isOrderActive = order_sell_id['isActive']
            if isOrderCancel is True:
                print('Order is cancelled!')
                break
            else:
                if market_price <= symbol_price_stop:
                    sell_template(symbol_to_roll, symbol_income_percent, symbol_stop)
                if isOrderActive is False:
                    buy_template(symbol_to_roll, symbol_income_percent, symbol_stop)
            time.sleep(1.500)
    except Exception as e:
        sys.exit(e)


def ask_income_percent():
    income_percent = input("Enter incoming percent of price you want to earn: ")
    if income_percent.isdigit():
        return float(income_percent) / 100


def ask_symbol_stop():
    symbol_stop = input('Enter stop-order percent of price you want to stop order, if it is triggered: ')
    if symbol_stop.isdigit():
        return float(symbol_stop) / 100


def launch_bot():
    """
    This function launch currency bot
    :return: that's function nothing to return
    """
    # Cancel all orders to avoid an exception
    client_trade.cancel_all_orders()

    # get_valid_currencies() outputs currencies and their amount, that have in trade wallet and possible to trade
    balance = get_valid_currencies()

    # Asks user about symbol he wants to roll and take profit/stop trigger
    symbol_to_roll = ask_user(balance)
    symbol_income_percent = ask_income_percent()
    symbol_stop = ask_symbol_stop()

    # Edits the requested response data
    symbol_to_roll_balance = get_valid_currencies()[symbol_to_roll.replace('-USDT', '')]
    symbol_price = float(check_price(symbol_to_roll))
    symbol_decimal = str(symbol_price)[::-1].find('.')
    symbol_price_sell = round(symbol_price + symbol_price * symbol_income_percent, symbol_decimal)

    # Creates an order, notifies our customer about created order and starts rolling
    order_sell_id = client_trade.create_limit_order(symbol_to_roll, 'sell', symbol_to_roll_balance,
                                                    symbol_price_sell)['orderId']
    symbol_price_stop = round(symbol_price - symbol_price * symbol_stop, symbol_decimal)
    print(f'Start rolling...\n{order_sell_id} is ordered for sale by'
          f' {round(symbol_price + symbol_price * symbol_income_percent, symbol_decimal)}')
    sell_currency(order_sell_id, symbol_to_roll, symbol_price_stop, symbol_income_percent, symbol_stop)


# Launch bot
if __name__ == "__main__":
    launch_bot()
