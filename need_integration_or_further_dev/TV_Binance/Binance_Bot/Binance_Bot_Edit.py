import redis

from time import sleep
import ccxt

from TV_Binance.Application_Handler import Application_Handler
from TV_Binance.Webhook_Handler import Webhook_Handler
from TV_Binance.debug_webhook_message import DEBUG_WEBHOOK_MESSAGE
from TV_Binance.tempt_utils import ensure_bool, _pubish_to_multiple_channels


class Binance_Bot(Application_Handler, Webhook_Handler):

    def __init__(self,
                 # redis_url,
                 bot_endpoints
                 ):

        # self.redis_url = redis_url
        # r = redis.from_url(self.redis_url)

        from os import getenv
        env_config = dict(
            WEBHOOK_PASSPHRASE=getenv("WEBHOOK_PASSPHRASE"),
            API_KEY=getenv("API_KEY"),
            SECRET_KEY=getenv("SECRET_KEY"),
            #
            ENABLE_RATE_LIMIT=getenv("ENABLE_RATE_LIMIT", default=True),
            EXCHANGE_TYPE=getenv("EXCHANGE_TYPE", default="future"),
            SANDBOX_MODE=getenv("SANDBOX_MODE", default=True),
            EXCHANGE="binance",  # do not change at this moment

            BOT_TEST_MODE=getenv("BOT_TEST_MODE",
                                 default=True if getenv("SANDBOX_MODE", default=True) else 'live_test'),
            VERBOSE=getenv("VERBOSE", default="DEBUG"),
        )

        self.test_mode = ensure_bool(env_config["BOT_TEST_MODE"], exception_values=["live_test"])

        assert self.test_mode in [True, False, "live_test"], "test_mode must be True, False or \"live_test\""
        assert env_config["SANDBOX_MODE"] in [True, False], "sandbox_mode must be True, False"

        # Initialize All Classes
        super().__init__(application_name=__name__,
                         test_mode=bool(self.test_mode) if self.test_mode != "live_test" else False,
                         verbose=env_config["VERBOSE"])

        # Prepare webhook
        # Endpoints can be passed in when we move towards expand the bot but will set only for our use case for now
        #   since we are only using one endpoint for now and the user can pass their custom bot function
        self.bot_endpoints = bot_endpoints

        # Client
        self.log = self.app.logger
        self.add_endpoints(endpoint_info_dict=self.bot_endpoints)

        # Exchange
        # self.exchange, self.webhook_passphrase = self.initialize_exchange(env_config)
        self.exchange, self.webhook_passphrase = self.initialize_exchange(env_config)

    def initialize_exchange(self, env_config):
        """
        Initialize the exchange and return the exchange object and webhook passphrase
        :param env_config:
        :return: exchange, webhook_passphrase
        """

        assert env_config, "env_config is wtf ... hold on??? check env_config"

        self.pretty_print(
            data=env_config,
            log_level="DEBUG"
        )
        self._exchange_name = env_config["EXCHANGE"]
        self.exchange_type = env_config["EXCHANGE_TYPE"]
        self._sandbox_mode = env_config["SANDBOX_MODE"]
        self.verbose = env_config["VERBOSE"]
        self.api_key = env_config["API_KEY"]
        self.secret_key = env_config["SECRET_KEY"]
        self.enable_rate_limit = env_config["ENABLE_RATE_LIMIT"]

        try:
            webhook_passphrase = env_config["WEBHOOK_PASSPHRASE"]

            exchange = self.get_exchange()
            try:
                assert webhook_passphrase, "Add the WEBHOOK_PASSPHRASE variable to your environment variables 🚨"
                assert exchange.apiKey, "Add the API_KEY variable to your environment variables 🚨"
                assert exchange.secret, "Add the SECRET_KEY variable to your environment variables 🚨"
            except AssertionError as e:
                self.log.error("Error during Exchange initialization: {}".format(e))
                raise e

            self.log.debug(f'{exchange.enableRateLimit = }')
            self.log.debug(f'{exchange.options = }')
            self.log.debug(f'{exchange.verbose = }')
            self.log.debug(f'{exchange.set_sandbox_mode = }')
            self.log.debug(f'exchange.fetch_balance() about to hit the API')
            balances = exchange.fetch_balance()
            self.log.debug(f'{balances = }')

            self.log.info(f'Asset Coins Free and Total 💱:')
            for coin in ["BNB", "BTC", "ETH", "USDT", "USDC", "BUSD"]:
                if balances[coin]['free'] > 0:
                    self.log.info(f'   {coin} : {balances[coin]}')

        except Exception as e:
            self.log.info(
                f"An error here is most likely due to a missing environment variables and/or incorrect API keys 🚨")
            self.log.info(f"Error initialising bot  {e}")
            raise e

        return exchange, webhook_passphrase

    def get_exchange(self):
        exchange = getattr(ccxt, self._exchange_name)({
            'apiKey': self.api_key,
            'secret': self.secret_key,
            'enableRateLimit': self.enable_rate_limit,
            'options': {
                'defaultType': self.exchange_type,
            },
        })
        exchange.set_sandbox_mode(self._sandbox_mode)
        exchange.verbose = True if self.verbose == ["DEBUG", "WARNING", "ERROR", "CRITICAL"] else False
        return exchange

    def tradingview_webhook_publisher(BOT):
        """Webhook to receive TradingView signals"""
        # Accept and Prepare Webhook
        message = BOT.fetch_new_webhook(clean_webhook=False)

        channel_endpoint_name = message["Account_Settings"]["channel_endpoint_name"]

        endpoint_dict = BOT.bot_endpoints[channel_endpoint_name]

        r = redis.from_url(endpoint_dict["redis_url"])
        import json

        if isinstance(endpoint_dict["channel_names"], list) and len(endpoint_dict["channel_names"]) != 1:
            _pubish_to_multiple_channels(r=r, channel_names=endpoint_dict["channel_names"], message=message)
        else:
            publisher = r.publish(channel=endpoint_dict["channel_names"][0], message=json.dumps(message))

        return message

    @staticmethod
    def sub(redis_url, channel_to_subscribe, function_to_call, **kwargs):
        r = redis.from_url(
            url=redis_url,
            decode_responses=True,
        )
        with r.pubsub() as pubsub:
            pubsub.subscribe(channel_to_subscribe)
            while True:
                # if not break_event.is_set(): break

                message = pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    try:
                        function_to_call(stream_message=message, **kwargs)
                    except Exception as e:
                        print(e)

    def test_binance_bot(self, channel_endpoint_name="tradingview_webhook_publisher", sleep_time=1):

        from time import perf_counter

        start = perf_counter()
        sleep(sleep_time)
        DEBUG_WEBHOOK_MESSAGE.update({'Signals': {"Buy": 1, "Minimal_Buy": 0, "Strong_Buy": 0, "Minimal_Strong_Buy": 0,
                                                  "Exit_Buy": 0, "Sell": 0, "Minimal_Sell": 0, "Strong_Sell": 0,
                                                  "Minimal_Strong_Sell": 0, "Exit_Sell": 0, "Clear_Orders": 0}})
        self.up(test_webhook_message=DEBUG_WEBHOOK_MESSAGE,
                test_endpoint_dict=self.bot_endpoints[channel_endpoint_name])
        sleep(sleep_time)
        DEBUG_WEBHOOK_MESSAGE.update({'Signals': {"Buy": 0, "Minimal_Buy": 0, "Strong_Buy": 0, "Minimal_Strong_Buy": 0,
                                                  "Exit_Buy": 0, "Sell": 1, "Minimal_Sell": 0, "Strong_Sell": 0,
                                                  "Minimal_Strong_Sell": 0, "Exit_Sell": 0, "Clear_Orders": 0}})
        self.up(test_webhook_message=DEBUG_WEBHOOK_MESSAGE,
                test_endpoint_dict=self.bot_endpoints[channel_endpoint_name])
        sleep(sleep_time)
        DEBUG_WEBHOOK_MESSAGE.update({'Signals': {"Buy": 0, "Minimal_Buy": 0, "Strong_Buy": 0, "Minimal_Strong_Buy": 0,
                                                  "Exit_Buy": 0, "Sell": 0, "Minimal_Sell": 0, "Strong_Sell": 0,
                                                  "Minimal_Strong_Sell": 0, "Exit_Sell": 1, "Clear_Orders": 0}})
        self.up(test_webhook_message=DEBUG_WEBHOOK_MESSAGE,
                test_endpoint_dict=self.bot_endpoints[channel_endpoint_name])
        sleep(sleep_time)
        DEBUG_WEBHOOK_MESSAGE.update({'Signals': {"Buy": 0, "Minimal_Buy": 0, "Strong_Buy": 0, "Minimal_Strong_Buy": 0,
                                                  "Exit_Buy": 0, "Sell": 0, "Minimal_Sell": 0, "Strong_Sell": 0,
                                                  "Minimal_Strong_Sell": 0, "Exit_Sell": 0, "Clear_Orders": 1}})
        self.up(test_webhook_message=DEBUG_WEBHOOK_MESSAGE,
                test_endpoint_dict=self.bot_endpoints[channel_endpoint_name])
        self.log.info(f"Time to run {perf_counter() - start} seconds")
        #
        # self.log.info(f"Binance Bot ping {self.breathing} 🤖")

        if self.test_mode:
            # Shut down the bot if testing
            self.down()


if __name__ == "__main__":
    #
    # Init Bot and Exchange
    binance_bot_client = Binance_Bot(tradingview_bot_function=premium_indicator_function)
    # assert binance_bot_client, "Binance Bot is not breathing right after initialization was attempted 🤖"

    app = binance_bot_client.app  # for gunicorn to run the app (see Procfile)
    #
    # Start App (begin listening) if not testing
    if binance_bot_client.test_mode:
        binance_bot_client.test_binance_bot(channel_endpoint_name="tradingview_webhook_publisher")
    else:
        binance_bot_client.up()
