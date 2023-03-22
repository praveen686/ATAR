"""Asynchronous Redis Stream Handler for Binance Websockets. This class is used to handle the Redis database in an
asynchronous way. It is used to store the data from the Binance Websocket API Manager and use the info for dashboards
and the strategy execution.
"""

# Import necessary libraries
import asyncio
import json
# from asyncio import sleep
from time import sleep
# import redis.asyncio as redis
import redis
# from unicorn_binance_websocket_api import BinanceWebSocketApiManager

from threading import Event

STOPWORD = "STOP REDIS STREAM"


class Binance_Stream_Handler:

    def __init__(self, redis_url: str = "redis://localhost"):
        self.redis_url = redis_url

    @staticmethod
    def _start_coroutines(coroutines: list):
        # use asyncio.gather to start N tasks at the same time thus allow for dynamic task creation
        results = asyncio.gather(
            *coroutines
        )
        return results

    def run_coroutines(self, coroutines: list):

        return asyncio.run(self._start_coroutines(coroutines=coroutines))

    @staticmethod
    def async_run(routine):
        return asyncio.run(routine)

    @staticmethod
    def create_task(task):
        return asyncio.create_task(task)

    @staticmethod
    def _pubish_to_multiple_channels(r: redis.Redis, channel_names, message):
        pipe = r.pipeline()  # creates a pipeline object that can be used to execute multiple commands in a single call to the server
        # Publish messages to multiple channels
        for channel_name in channel_names:
            pipe.publish(channel_name, json.dumps(message))
        oks = pipe.execute()
        for ok in oks:
            try:
                assert ok
                print(f"Published to channel {channel_names} --> {message}")
            except Exception as e:
                print(f"Error publishing to channel {channel_name}: {e}")

    def binance_websocket_publisher(self, channel_names: list,
                                    binance_websocket_api_manager,
                                    binance_stream_infos: dict,
                                    sleep_time: float = 0.01,
                                    create_thread=False,
                                    daemon=True,
                                    break_event=None,
                                    ):
        """This function is used to publish the data from the Binance Websocket API Manager to the Redis database
        through PUB/SUB channels

        :param channel_names: The names of the channels to publish to (list)
        :       Example: ["channel_1", "channel_2"] or
        :       WILL NOT CHANGE ACCORDING TO THE STREAMS CREATED, EVERY CHANNEL WILL BE PUBLISHED WITH THE SAME DATA!!!
        :param binance_websocket_api_manager: The Binance Websocket API Manager (BinanceWebSocketApiManager)
        :param binance_stream_infos: The info for the Binance Websocket API Manager (dict)
        :       Example:
        :       binance_stream_infos = {
        :           "stream_1": {
        :               "channels": ["trade"],
        :               "markets": ["BTCUSDT"]
        :           },
        :           "stream_2": {
        :               "channels": ["trade", "kline_1m"],
        :               "markets": ["ETHUSDT"]
        :           },
        :           "stream_3": {
        :               "channels": ["trade", "kline_1m"],
        :               "markets": ["ETHUSDT", "BTCUSDT"]
        :           }
        :       }
        :param sleep_time: The time to sleep between each iteration (float)
        :param create_thread: Whether to create a thread for the function (bool)
        :param daemon: Whether the thread is a daemon thread (bool)
        """

        r = redis.from_url(self.redis_url)

        for key_name, ch_m_values in binance_stream_infos.items():
            print(f'Registering {key_name} : {ch_m_values} Websocket Streams')
            binance_websocket_api_manager.create_stream(
                ch_m_values["channels"], ch_m_values["markets"], output="UnicornFy")

        def _binance_websocket_publisher(r: redis.Redis, channel_names: list,
                                         binance_websocket_api_manager,
                                         sleep_time: float = 0.01):
            websocket_stream_gate_bool = True
            while websocket_stream_gate_bool:
                if not break_event.is_set(): break

                # Middleman
                if binance_websocket_api_manager.is_manager_stopping(): websocket_stream_gate_bool = False
                #
                new_stream_data = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
                if new_stream_data is False:
                    sleep(sleep_time)
                else:
                    # Publish messages to the channels
                    # r.publish(channel_names[0], json.dumps(new_stream_data))
                    self._pubish_to_multiple_channels(r=r, channel_names=channel_names, message=new_stream_data)




        if not create_thread:
            _binance_websocket_publisher(r=r, channel_names=channel_names,
                                         binance_websocket_api_manager=binance_websocket_api_manager,
                                         sleep_time=sleep_time)
            return None
        else:
            import threading
            t = threading.Thread(target=_binance_websocket_publisher,
                                 args=(r, channel_names, binance_websocket_api_manager, sleep_time),
                                 daemon=daemon)
            t.start()
            return t

    def binance_websocket_subscriber(self, break_event, channel_names: list,
                                     binance_subscriber_function,
                                     # must be a function and accept stream_data as input
                                     binance_subscriber_function_kwargs: dict = None,
                                     create_thread: bool = False,
                                     daemon: bool = True):
        r = redis.from_url(self.redis_url)

        def _binance_websocket_subscriber(r: redis.Redis, channel_names: list,
                                          binance_subscriber_function,
                                          # must be a function and accept stream_data as input
                                          binance_subscriber_function_kwargs: dict = None,
                                          ):
            with r.pubsub() as pubsub:
                pubsub.subscribe(*channel_names)

                while True:
                    if not break_event.is_set(): break

                    message = pubsub.get_message(ignore_subscribe_messages=True)
                    if message is not None:
                        try:
                            binance_subscriber_function(stream_message=message["data"].decode(),
                                                        **binance_subscriber_function_kwargs)
                            if message["data"].decode() == STOPWORD: break
                        except Exception as e:
                            print(e)

        if not create_thread:
            return _binance_websocket_subscriber(r=r, channel_names=channel_names,
                                                 binance_subscriber_function=binance_subscriber_function,
                                                 binance_subscriber_function_kwargs=binance_subscriber_function_kwargs)
        else:
            import threading
            t = threading.Thread(target=_binance_websocket_subscriber,
                                 args=(
                                     r, channel_names, binance_subscriber_function, binance_subscriber_function_kwargs),
                                 daemon=daemon)
            t.start()
            return t


if __name__ == "__main__":
    # Set up the Binance Websocket Streams
    binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures-testnet")
    BINANCE_STREAM_INFOS = dict(
        stream_1=dict(
            markets=["btcusdt"],
            channels=["kline_1m"],
        ),
    )
    REDIS_URL = "redis://localhost"
    PUB_CHANNELS = ['kline_1m_btcusdt']
    SUB_CHANNELS = ['kline_1m_btcusdt']
    TEST_PRINT_FUNCTION = lambda stream_message, test_arg: print(
        f"(Reader) Message Received: {stream_message} with {test_arg}"
    )
    binance_subscriber_function_kwargs = {"test_arg": "test"}
    #
    bsh = Binance_Stream_Handler(redis_url=REDIS_URL)  # Create the Binance Stream Handler

    bsh.binance_websocket_publisher(
        channel_names=PUB_CHANNELS,
        binance_websocket_api_manager=binance_websocket_api_manager,
        binance_stream_infos=BINANCE_STREAM_INFOS,
        create_thread=True,
        daemon=True,

    )

    bsh.binance_websocket_subscriber(
        channel_names=SUB_CHANNELS,
        binance_subscriber_function=TEST_PRINT_FUNCTION,
        binance_subscriber_function_kwargs=binance_subscriber_function_kwargs,
        create_thread=True,
        daemon=True,
    )

    print("Outside of the loop")
