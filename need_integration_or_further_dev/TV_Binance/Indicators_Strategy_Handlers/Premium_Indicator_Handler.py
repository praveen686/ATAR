def get_side_of_position_to_enter_or_exit(webhook_signals, position_amount):
    # fixme currently written explicity and expanded for clarity, this can be optimised but left for now as it will be
    #   deprecated in the next version

    # Check if we are in a position and if we are, what side of the position we are in
    long_position_open = position_amount > 0
    short_position_open = position_amount < 0

    # Determine if we are entering
    if webhook_signals["Buy"] or webhook_signals["Strong_Buy"]:
        side_of_position_to_enter = "buy"
    elif webhook_signals["Sell"] or webhook_signals["Strong_Sell"]:
        side_of_position_to_enter = "sell"
    else:
        side_of_position_to_enter = None

    # Determine if we are exiting and check we have a position to exit
    # fixme This is not currently being used by the customer, but is here as placeholder for future use cases
    if webhook_signals["Exit_Buy"] and long_position_open:
        side_of_position_to_exit = "buy"
    elif webhook_signals["Exit_Sell"] and short_position_open:
        side_of_position_to_exit = "sell"
    else:
        side_of_position_to_exit = None

    # Check if we are exiting current position and entering a new position in the same candle
    if short_position_open and side_of_position_to_enter == 'buy':
        side_of_position_to_exit = 'sell'
    elif long_position_open and side_of_position_to_enter == 'sell':
        side_of_position_to_exit = 'buy'
    else:
        side_of_position_to_exit = None if side_of_position_to_exit is None else side_of_position_to_exit

    # fixme  hotfix to prevent hitting the max open orders limit of binance
    #   current_position_info = BOT.exchange.fapiPrivate_get_positionrisk({"symbol": symbol})[0]
    #   current_position_amount = float(current_position_info["positionAmt"])
    if long_position_open and side_of_position_to_enter == 'buy':
        side_of_position_to_enter = None
    elif short_position_open and side_of_position_to_enter == 'sell':
        side_of_position_to_enter = None

    if webhook_signals["Clear_Orders"]:
        cancel_all_symbol_open_orders = True
    else:
        cancel_all_symbol_open_orders = False

    return side_of_position_to_enter, side_of_position_to_exit, cancel_all_symbol_open_orders


def premium_indicator_function(BOT, webhook_message):
    """
    This is the webhook that will be called by the TradingView Alert. It will receive the data from the alert and then
    place the order on the Binance exchange.
    :return:
    """

    # Get Symbol
    symbol = webhook_message["Order_Settings"]["binance_symbol"]

    # > Order Settings
    order_type = webhook_message["Order_Settings"]["order_type"]
    #
    #   --take_profit, stop_loss, trailing_stop specific settings--
    take_profit = webhook_message["Trade_Management"]["position_boundaries"].get("take_profit", None)
    stop_loss = webhook_message["Trade_Management"]["position_boundaries"].get("stop_loss", None)

    trailing_stop_loss_percentage = webhook_message["Trade_Management"]["trailing_stop_loss"].get(
        "trailing_stop_loss_percentage", None)
    trailing_stop_loss_activation_percentage = webhook_message["Trade_Management"]["trailing_stop_loss"].get(
        "trailing_stop_loss_activation_percentage", None)

    DCA_bool = webhook_message["Trade_Management"]["dca_entries"].get("on_off", None)
    DCA_total_amount = webhook_message["Trade_Management"]["dca_entries"].get("total_amount", None)
    DCA_opposite_boundary_percentage = webhook_message["Trade_Management"]["dca_entries"].get(
        "opposite_boundary_percentage",
        None)
    DCA_number_of_steps = webhook_message["Trade_Management"]["dca_entries"].get("number_of_steps", None)

    #
    #   --limit order specific settings--
    max_orderbook_depth = webhook_message["Order_Settings"].get("max_orderbook_depth", None)
    min_orderbook_price_offset = webhook_message["Order_Settings"].get("min_orderbook_price_offset", None)
    max_orderbook_price_offset = webhook_message["Order_Settings"].get("max_orderbook_price_offset", None)
    limit_forced_offset = webhook_message["Order_Settings"].get("limit_forced_offset", None)

    # Get info need for order placement settings
    cash_bet_ammount = webhook_message["Order_Settings"].get("cash_bet_amount", None)
    max_account_risk_per_trade = webhook_message["Account_Settings"].get("max_account_risk_per_trade", None)
    last_price = BOT.exchange.fetch_ticker(symbol)["last"]
    #
    USDT_free_balance = BOT.exchange.fetch_free_balance()["USDT"]
    account_balance_available_for_trade = USDT_free_balance * max_account_risk_per_trade
    cash_amt_for_trade = account_balance_available_for_trade if account_balance_available_for_trade < cash_bet_ammount else cash_bet_ammount

    # Extra exchange settings
    leverage = webhook_message["Order_Settings"].get("leverage", None)
    free_balance_trading_symbol = BOT.exchange.fetch_free_balance()[symbol.split("USDT")[0]]  # e.g. BTC or ETH
    current_position_info = BOT.exchange.fapiPrivate_get_positionrisk({"symbol": symbol})[0]
    current_position_amount = float(current_position_info["positionAmt"])

    # todo can be moved to webhook checks
    if BOT.exchange.options["defaultType"] == "future" and leverage != current_position_info["leverage"]:
        BOT.exchange.fapiPrivate_post_leverage({"symbol": symbol, "leverage": leverage})
    elif BOT.exchange.options["defaultType"] == "spot":
        assert leverage == 1, "Leverage must be 1 for spot trading, not changing to default leverage of 1 to allow user " \
                              "to check for mistakes or desired outcome"

    # todo should check the cap/floor ratio to ensure it is within the range of the exchange and the user's risk
    #  tolerance
    print("\n")
    BOT.pretty_print({
        "order_type": order_type,
        "take_profit": take_profit,
        "stop_loss": stop_loss,
        "trailing_stop_loss_percentage": trailing_stop_loss_percentage,
        "trailing_stop_loss_activation_percentage": trailing_stop_loss_activation_percentage,
        "max_orderbook_depth": max_orderbook_depth,
        "min_orderbook_price_offset": min_orderbook_price_offset,
        "max_orderbook_price_offset": max_orderbook_price_offset,
        "limit_forced_offset": limit_forced_offset,
        "cash_bet_ammount": cash_bet_ammount,
        "max_account_risk_per_trade": max_account_risk_per_trade,
        "last_price": last_price,
        "USDT_free_balance": USDT_free_balance,
        "account_balance_available_for_trade": account_balance_available_for_trade,
        "cash_amt_for_trade": cash_amt_for_trade,
        "leverage": leverage,
        "free_balance_trading_symbol": free_balance_trading_symbol,
        "current_position_info": current_position_info,
        "current_position_amount": current_position_amount,
    })

    print("\n")

    # Size of the order in the trading symbol (e.g. {trade_size} BTC or {trade_size} ETH) not USDT
    trade_size = ((cash_amt_for_trade / last_price) * leverage)

    if DCA_bool == True:
        if DCA_total_amount == 0:
            DCA_total_amount = trade_size
            print(f'{trade_size = }')
            print(f'{DCA_total_amount = }')

        BOT.log.info(
            f'The initial trade size is {trade_size} {symbol.split("USDT")[0]}'
            f'DCA is enabled, total amount is {DCA_total_amount} which will be split into {DCA_number_of_steps}'
            f' ${DCA_total_amount / DCA_number_of_steps} per order')
    else:
        DCA_total_amount = None
        BOT.log.info(f'DCA is disabled, total amount is {trade_size}')

    side_of_position_to_enter, side_of_position_to_exit, cancel_all_symbol_open_orders = get_side_of_position_to_enter_or_exit(
        webhook_signals=webhook_message["Signals"], position_amount=current_position_amount)
    try:
        action_present = side_of_position_to_exit or side_of_position_to_enter or cancel_all_symbol_open_orders
        assert action_present, "No entry or exit signal detected, please check your TradingView or get_side_of_position_to_enter_or_exit function"
        assert side_of_position_to_exit in ["buy", "sell"] or side_of_position_to_enter in ["buy", "sell"] or \
               cancel_all_symbol_open_orders == True, \
            "side_of_position_to_exit/side_of_position_to_enter must be 'buy' or 'sell'"

        #
    except AssertionError as assertion_error:
        BOT.log.info(f'{side_of_position_to_enter = }')
        BOT.log.info(f'{side_of_position_to_exit = }')
        raise assertion_error

    orders = {}  # dict to store the orders placed during this bot call

    '''Cancel all open orders if cancel_all_symbol_open_orders is True'''
    if cancel_all_symbol_open_orders:
        orders["open_orders_cancelled"] = BOT.cancel_all_symbol_open_orders(symbol=symbol)

    '''Exit position if exit signal or flipping position side is defined or if contrarian_order is True'''
    print(f'{webhook_message["Signals"]  =}')
    print(f'{side_of_position_to_exit  =}')
    print(f'{side_of_position_to_enter  =}')
    print(f'{cancel_all_symbol_open_orders  =}')
    if side_of_position_to_exit:
        orders["closed_position"] = BOT.market_close_position(
            order_json=dict(
                side=side_of_position_to_exit,
                amount=abs(current_position_amount),
                info=dict(symbol=symbol)))
        # orders["closed_position"] = BOT.close_position(
        #     position_id={BOT.exchange.fetch_positions(symbols=[symbol])[0]["id"]})

    if side_of_position_to_enter:
        orders["order_placed"] = BOT.open_position(last_price=last_price, side=side_of_position_to_enter,
                                                   quantity=trade_size, symbol=symbol, order_type=order_type,
                                                   position_params={}, max_orderbook_depth=max_orderbook_depth,
                                                   min_orderbook_price_offset=min_orderbook_price_offset,
                                                   max_orderbook_price_offset=max_orderbook_price_offset,
                                                   limit_forced_offset=limit_forced_offset, take_profit=take_profit,
                                                   stop_loss=stop_loss, callbackRate=trailing_stop_loss_percentage,
                                                   activation_percentage=trailing_stop_loss_activation_percentage,
                                                   #
                                                   # Unpredictable behaviour when using DCA, use at your own risk
                                                   DCA_bool=DCA_bool, DCA_total_amount=DCA_total_amount,
                                                   DCA_opposite_boundry_percentage=DCA_opposite_boundary_percentage,
                                                   DCA_number_of_steps=DCA_number_of_steps
                                                   )

    # return orders if orders else "No entry or exit signal detected, please check your TradingView or " \
    #                              "get_side_of_position_to_enter_or_exit function"

    return orders
