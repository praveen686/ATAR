def start_binance_bot():
    # Init Bot and Exchange
    from BOTs.Binance_Bot.Binance_Bot import Binance_Bot
    assert Binance_Bot.breathing == False, "Binance Bot is already breathing 🤖 ... check your code"
    from Indicators_Strategy_Handlers.Premium_Indicator_Handler import premium_indicator_function
    binance_bot_client = Binance_Bot(tradingview_bot_function=premium_indicator_function)
    # assert binance_bot_client, "Binance Bot is not breathing right after initialization was attempted 🤖"

    app = binance_bot_client.app  # for gunicorn to run the app (see Procfile)
    #
    # Start App (begin listening) if not testing
    if binance_bot_client.test_mode:
        binance_bot_client.test_binance_bot()
    else:
        # binance_bot_client.up()
        binance_bot_client.test_binance_bot()

    #
    binance_bot_client.log.info(f"Binance Bot ping {binance_bot_client.breathing} 🤖")

    if binance_bot_client.test_mode:
        # Shut down the bot if testing
        binance_bot_client.down()

    return app


if __name__ == "BOTs.run_bot":
    app = start_binance_bot()
