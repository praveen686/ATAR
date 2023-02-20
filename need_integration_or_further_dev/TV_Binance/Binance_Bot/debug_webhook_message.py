DEBUG_WEBHOOK_MESSAGE = {
    'Account_Settings': {
        # This is the passphrase that you set in the TradingView Alert
        "passphrase": "8j4tr38j8jfsvdap98g",
        # This is the maximum amount of risk that you want to take on the trade (Max percentage of free balance in
        # account to use for a given trade. If max_account_risk_per_trade < cash_bet_amount, this value will be used
        # instead when computing trade size)
        "max_account_risk_per_trade": 1,  # 0 < max_account_risk_per_trade <= 1

    },
    "Order_Settings": {
        # This is the symbol that you want to trade on Binance
        "binance_symbol": "BTCUSDT",
        "leverage": 1,
        # This is the amount of cash that you want to bet on the trade fixed usdt ammount per trade aka as close as
        # the fluctuation in price allows
        "cash_bet_amount": 50,
        # "order_type": "market",
        "order_type": "limit",

        # Note these won't matter if order_type is market
        # todo need to allow for partial fills, however client does not want this at the moment
        "max_orderbook_depth": 10,
        "max_orderbook_price_offset": 1,
        "min_orderbook_price_offset": 0,
        "limit_forced_offset": 0,  # is either this or the above 3 settings

        # Test Webhook (used for testing, and will not place orders on Binance or testnet, will only log to console)
        # "test_orders": 0  # -1 or 0 = off, 1 = on # todo add this
    },

    "Trade_Management": {
        # "persistent_checks": 0,  # -1 or 0 = off, 1 = on # todo add this
        # "place_orders_in_batch": 0,  # todo lets reduce the number of api calls by utilizing batch orders. add tp,sl, tsl batch orders
        "position_boundaries": {
            "take_profit": 0.25,
            "stop_loss": 0.25
        },
        "trailing_stop_loss": {
            # "trailing_stop_loss_type": "percentage (dec)", # todo add this
            "trailing_stop_loss_percentage": -1,
            "trailing_stop_loss_activation_percentage": -1
        },
        "dca_entries": {
            "on_off": 1,
            "total_amount": 0,  # defaults to trade size and then split into number of steps
            "opposite_boundary_percentage": 0.01,
            "number_of_steps": 2
        }
    },

    # Tradingview Premium Indicator Alert will send the following data:
    'Signals': {
        "Buy": 0,
        "Minimal_Buy": 0,
        "Strong_Buy": 0,
        "Minimal_Strong_Buy": 0,
        "Exit_Buy": 0,
        "Sell": 0,
        "Minimal_Sell": 0,
        "Strong_Sell": 0,
        "Minimal_Strong_Sell": 0,
        "Exit_Sell": 0,
        "Clear_Orders": 0
    }
}

# tv_version = {
#     'Account_Settings': {
#         "passphrase": "8j4tr38j8jfsvdap98g",
#         "max_account_risk_per_trade": 1,
#     },
#     "Order_Settings": {
#         "binance_symbol": "BTCUSDT",
#         "leverage": 1,
#         "cash_bet_amount": 50,
#         "order_type": "limit",
#         "max_orderbook_depth": 10,
#         "max_orderbook_price_offset": 1,
#         "min_orderbook_price_offset": 0,
#         "limit_forced_offset": 0
#     },
#
#     "Trade_Management": {
#         "persistent_checks": 0,
#         "position_boundaries": {
#             "take_profit": 0.25,
#             "stop_loss": 0.25
#         },
#         "trailing_stop_loss": {
#             # "trailing_stop_loss_type": "percentage (dec)", # todo add this
#             "trailing_stop_loss_percentage": -1,
#             "trailing_stop_loss_activation_percentage": -1
#         },
#         "dca_entries": {
#             "on_off": 0,
#             "total_amount": 0,  # defaults to trade size and then split into number of steps
#             "opposite_boundary_percentage": 0.01,
#             "number_of_steps": 2
#         }
#     },
#     "Signals": {
#         "Buy": {{plot("Buy")}},
#         "Minimal_Buy": {{plot("Minimal Buy")}},
#         "Strong_Buy": {{plot("Strong Buy")}},
#         "Minimal_Strong_Buy": {{plot("Minimal Strong Buy")}},
#         "Exit_Buy": {{plot("Exit Buy")}},
#         "Sell": {{plot("Sell")}},
#         "Minimal_Sell": {{plot("Minimal Sell")}},
#         "Strong_Sell": {{plot("Strong Sell")}},
#         "Minimal_Strong_Sell": {{plot("Minimal Strong Sell")}},
#         "Exit_Sell": {{plot("Exit Sell")}}
#     }
# }
