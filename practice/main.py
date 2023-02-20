#!/usr/bin/env python3
from live_pipeline_build import live_pipeline_build
import numpy as np

if __name__ == "__main__":

    # from TV_Binance.Binance_Bot_Edit import Binance_Bot
    #
    # redis_url = "redis://localhost:6379"
    # channel_name = "tradingview_webhook_publisher"
    #
    # binance_bot_client = Binance_Bot(
    #     bot_endpoints=dict(
    #         tradingview_webhook_publisher=dict(
    #             rule='/tradingview_webhook_publisher',
    #             function="tradingview_webhook_publisher",  # function but if string it searches for it in the class
    #             methods=['POST'],
    #             #
    #             # If redis
    #             redis_url=redis_url,
    #             channel_names=[channel_name],
    #         ),
    #     ),
    # )
    #
    # app = binance_bot_client.app  # for gunicorn to run the app (see Procfile)
    # #
    # # Start App (begin listening) if not testing
    # if binance_bot_client.test_mode:
    #     # from TV_Binance.Redis_Binance_Stream_Handler import Binance_Stream_Handler
    #     #
    #     # Run corrutine
    #     # streamer = Binance_Stream_Handler(redis_url=redis_url)
    #     #
    #     # streamer.run_coroutines(coroutines=[
    #     #     binance_bot_client.test_binance_bot(),
    #     #     binance_bot_client.sub(
    #     #         redis_url=redis_url,
    #     #         channel_to_subscribe=channel_name,
    #     #         function_to_call=lambda stream_message: print(f'{stream_message = }'),
    #     #         **{})
    #     #     # sub()
    #     # ])
    #     threading.Thread(target=binance_bot_client.test_binance_bot,
    #                      args=("tradingview_webhook_publisher",5)
    #                      ,daemon=True).start()
    #     threading.Thread(target=binance_bot_client.sub,
    #                      kwargs=dict(
    #                          redis_url=redis_url,
    #                          channel_to_subscribe=channel_name,
    #                          function_to_call=lambda stream_message: print(f'{stream_message = }'),
    #                          **{}), daemon=True
    #                      ).start()
    #     # binance_bot_client.test_binance_bot()
    # else:
    #     binance_bot_client.up()
    # import vectorbtpro as vbtpro
    """# Build the node"""
    node = live_pipeline_build()

    try:
        # Start the node
        node.start()
    finally:
        # Stop and dispose of the node with SIGINT/CTRL+C
        node.dispose()
