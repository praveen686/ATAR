import nautilus_trader as genie_trader
import pandas as pd


def live_pipeline_build():
    from decimal import Decimal

    from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
    from nautilus_trader.adapters.binance.config import BinanceDataClientConfig
    from nautilus_trader.adapters.binance.config import BinanceExecClientConfig
    from nautilus_trader.adapters.binance.factories import BinanceLiveDataClientFactory
    from nautilus_trader.adapters.binance.factories import BinanceLiveExecClientFactory
    from nautilus_trader.config import CacheDatabaseConfig
    from nautilus_trader.config import InstrumentProviderConfig
    from nautilus_trader.config import TradingNodeConfig
    from nautilus_trader.config.live import LiveExecEngineConfig
    from nautilus_trader.live.node import TradingNode

    from strategy_practice import Practice_Strat_Config, Practice_Strat
    # from genie_trader.examples.strategies.ema_cross_trailing_stop import EMACrossTrailingStop

    # *** THIS IS A TEST STRATEGY WITH NO ALPHA ADVANTAGE WHATSOEVER. ***
    # *** IT IS NOT INTENDED TO BE USED TO TRADE LIVE WITH REAL MONEY. ***

    # *** THIS INTEGRATION IS STILL UNDER CONSTRUCTION. ***
    # *** CONSIDER IT TO BE IN AN UNSTABLE BETA PHASE AND EXERCISE CAUTION. ***

    # Configure the trading node
    config_node = TradingNodeConfig(
        trader_id="TESTER-001",
        log_level="DEBUG",
        exec_engine=LiveExecEngineConfig(
            reconciliation=True,
            reconciliation_lookback_mins=1440,
        ),
        # cache_database=CacheDatabaseConfig(type="in-memory"),
        # cache_database=CacheDatabaseConfig(type="redis"),
        cache_database=CacheDatabaseConfig(type="redis", host="redis-16090.c114.us-east-1-4.ec2.cloud.redislabs.com",
                                           port=16090,
                                           username="default", password="OlRtlXKrSkGzmvhiLgxjDgS4cp2PkIJl",
                                           ssl=False, flush=True),
        data_clients={
            "BINANCE": BinanceDataClientConfig(
                api_key="316ee06e009b0ec07b92d15328bed7f0a92c7e1ddb2ce8a755273a6d4f91c802",
                # "YOUR_BINANCE_TESTNET_API_KEY"
                api_secret="e56b5fbc30dee0b4eb951933b39bc6eb4864a7ae2b60768a6697960b3ff5e838",
                # "YOUR_BINANCE_TESTNET_API_SECRET"
                account_type=BinanceAccountType.FUTURES_USDT,
                base_url_http=None,  # Override with custom endpoint
                base_url_ws=None,  # Override with custom endpoint
                us=False,  # If client is for Binance US
                testnet=True,  # If client uses the testnet
                # instrument_provider=InstrumentProviderConfig(load_all=True),
                instrument_provider=InstrumentProviderConfig(
                    load_ids=("BTCUSDT-PERP.BINANCE", "ETHUSDT-PERP.BINANCE")
                    # load_all=True
                )
            ),
        },
        exec_clients={
            "BINANCE": BinanceExecClientConfig(
                api_key="316ee06e009b0ec07b92d15328bed7f0a92c7e1ddb2ce8a755273a6d4f91c802",
                # "YOUR_BINANCE_TESTNET_API_KEY"
                api_secret="e56b5fbc30dee0b4eb951933b39bc6eb4864a7ae2b60768a6697960b3ff5e838",
                # "YOUR_BINANCE_TESTNET_API_SECRET"
                account_type=BinanceAccountType.FUTURES_USDT,
                base_url_http=None,  # Override with custom endpoint
                base_url_ws=None,  # Override with custom endpoint
                us=False,  # If client is for Binance US
                testnet=True,  # If client uses the testnet
                # instrument_provider=InstrumentProviderConfig(load_all=True),
                instrument_provider=InstrumentProviderConfig(
                    load_ids=("BTCUSDT-PERP.BINANCE", "ETHUSDT-PERP.BINANCE")
                    # load_all=True

                )
            ),
        },
        timeout_connection=5.0,
        timeout_reconciliation=5.0,
        timeout_portfolio=5.0,
        timeout_disconnection=5.0,
        timeout_post_stop=2.0,
    )
    # Instantiate the node with a configuration
    node = TradingNode(config=config_node)

    # Configure your strategy
    strat_config = Practice_Strat_Config(
        instrument_id="BTCUSDT-PERP.BINANCE",
        bar_type="BTCUSDT-PERP.BINANCE-1-MINUTE-LAST-EXTERNAL",
        trade_size=Decimal("0.001"),

        fast_ema_period=3,
        slow_ema_period=14,
        atr_period=5,
        trailing_atr_multiple=1.5,
        trailing_offset_type="BASIS_POINTS",
        trigger_type="LAST_TRADE",

        # bar_type="BTCUSDT-PERP.BINANCE-1000-TICK[LAST]-INTERNAL",
        # trade_size=Decimal(0.001),
        order_id_tag="001",
    )

    # Instantiate your strategy
    strategy = Practice_Strat(config=strat_config)

    # Add your strategies and modules
    node.trader.add_strategy(strategy)

    # #############
    # # Configure your strategy
    # strat_config = Practice_Strat_Config(
    #     instrument_id="ETHUSDT-PERP.BINANCE",
    #     bar_type="ETHUSDT-PERP.BINANCE-1-MINUTE-LAST-EXTERNAL",
    #     trade_size=Decimal("0.007"),
    #
    #     fast_ema_period=3,
    #     slow_ema_period=14,
    #     atr_period=5,
    #     trailing_atr_multiple=1.5,
    #     trailing_offset_type="BASIS_POINTS",
    #     trigger_type="LAST_TRADE",
    #     order_id_tag="002",
    #     activation_percentage=0.001,
    # )
    #
    # # Instantiate your strategy
    # strategy = Practice_Strat(config=strat_config)
    #
    # # Add your strategies and modules
    # node.trader.add_strategy(strategy)
    # #############

    # Register your client factories with the node (can take user defined factories)
    node.add_data_client_factory("BINANCE", BinanceLiveDataClientFactory)
    node.add_exec_client_factory("BINANCE", BinanceLiveExecClientFactory)
    node.build()

    return node


# Stop and dispose of the node with SIGINT/CTRL+C
if __name__ == "__main__":
    node = live_pipeline_build()

    try:
        node.run()
    finally:
        node.dispose()
