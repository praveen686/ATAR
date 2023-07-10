#!/usr/bin/env python3
import os
from decimal import Decimal

from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
from nautilus_trader.adapters.binance.config import BinanceDataClientConfig
from nautilus_trader.adapters.binance.config import BinanceExecClientConfig
from nautilus_trader.adapters.binance.factories import BinanceLiveDataClientFactory, BinanceLiveExecClientFactory
from nautilus_trader.config import CacheDatabaseConfig
from nautilus_trader.config import InstrumentProviderConfig
from nautilus_trader.config import LiveExecEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.live.node import TradingNode

import sys

from Modules.Strategies.MarketVolatilityCatcher import MarketVolatilityCatcher, MarketVolatilityCatcherConfig, \
    TWAPExecAlgorithm

sys.path.append("/home/ruben/PycharmProjects/Genie-Trader/Modules/Nodes/examples/strategies")
sys.path.append("/home/ruben/PycharmProjects/Genie-Trader/Modules/Nodes/examples/algorithms")


# read ../.env file and set environment variables
with open("/home/ruben/PycharmProjects/Genie-Trader/Modules/Nodes/.env") as f:
    for line in f:
        key, value = line.strip().split("=")
        if key not in os.environ:
            print(f"Setting environment variable: {key}=****")
            os.environ[key] = value

# Configure the trading node
config_node = TradingNodeConfig(
    trader_id="TESTER-001",
    logging=LoggingConfig(
        log_level="INFO",
        # log_level_file="DEBUG",
        # log_file_format="json",
    ),
    exec_engine=LiveExecEngineConfig(
        reconciliation=True,
        reconciliation_lookback_mins=1440,
    ),
    cache_database=CacheDatabaseConfig(type="in-memory"),
    data_clients={
        "BINANCE": BinanceDataClientConfig(
            # api_key=None,  # "YOUR_BINANCE_TESTNET_API_KEY"
            # api_secret=None,  # "YOUR_BINANCE_TESTNET_API_SECRET"
            account_type=BinanceAccountType.USDT_FUTURE,
            base_url_http=None,  # Override with custom endpoint
            base_url_ws=None,  # Override with custom endpoint
            us=False,  # If client is for Binance US
            testnet=True,  # If client uses the testnet
            instrument_provider=InstrumentProviderConfig(load_all=True),
        ),
    },
    exec_clients={
        "BINANCE": BinanceExecClientConfig(
            # api_key=None,  # "YOUR_BINANCE_TESTNET_API_KEY"
            # api_secret=None,  # "YOUR_BINANCE_TESTNET_API_SECRET"
            account_type=BinanceAccountType.USDT_FUTURE,
            base_url_http=None,  # Override with custom endpoint
            base_url_ws=None,  # Override with custom endpoint
            us=False,  # If client is for Binance US
            testnet=True,  # If client uses the testnet
            instrument_provider=InstrumentProviderConfig(load_all=True),
        ),
    },
    timeout_connection=10.0,
    timeout_reconciliation=10.0,
    timeout_portfolio=10.0,
    timeout_disconnection=10.0,
    timeout_post_stop=5.0,
)
# Instantiate the node with a configuration
node = TradingNode(config=config_node)

# Register your client factories with the node (can take user defined factories)
node.add_data_client_factory("BINANCE", BinanceLiveDataClientFactory)
node.add_exec_client_factory("BINANCE", BinanceLiveExecClientFactory)

# Instruments to trade
instruments_temp_dict = dict(
    BTCUSDT_PERP_BINANCE=["BTCUSDT-PERP.BINANCE", Decimal(str(0.001 * 5)), "1-MINUTE-LAST-EXTERNAL"],
    # BTCUSDT_PERP_BINANCE=["BTCUSDT-PERP.BINANCE", Decimal(str(0.001 * 5)), "5-SECOND-MID-INTERNAL"],
    # ETHUSDT_PERP_BINANCE=["ETHUSDT-PERP.BINANCE", Decimal(str(0.003 * 5)), "5-SECOND-MID-INTERNAL"],
    # BCHUSDT_PERP_BINANCE=["BCHUSDT-PERP.BINANCE", Decimal(str(0.053 * 3)), "5-TICK-LAST-INTERNAL"],
    # LTCUSDT_PERP_BINANCE=["LTCUSDT-PERP.BINANCE", Decimal(str(0.068 * 3)), "5-TICK-LAST-INTERNAL"],
)

# Add your strategies to the node
for instrument, trade_size, bar_type in instruments_temp_dict.values():
    # Configure your strategy
    strat_config = MarketVolatilityCatcherConfig(
        strategy_id=instrument,
        instrument_id=instrument,
        external_order_claims=[instrument],
        bar_type=f"{instrument}-{bar_type}",
        atr_period=7,
        atr_multiple=0.5,
        trade_size=trade_size,
    )
    # Instantiate your strategy
    strategy = MarketVolatilityCatcher(config=strat_config)

    # strat_config = EMACrossTWAPConfig(
    #     strategy_id=instrument,
    #     instrument_id=instrument,
    #     external_order_claims=[instrument],
    #     bar_type=f"{instrument}-{bar_type}",
    #     fast_ema_period=7,
    #     slow_ema_period=14,
    #     twap_horizon_secs=5,
    #     twap_interval_secs=0.5,
    #     trade_size=Decimal("0.100"),
    # )
    # # Instantiate your strategy and execution algorithm
    # strategy = EMACrossTWAP(config=strat_config)

    # Add your strategies and modules
    node.trader.add_strategy(strategy)

# Configure your execution algorithm
exec_algorithm = TWAPExecAlgorithm()

# Add execution algorithm
node.trader.add_exec_algorithm(exec_algorithm)

node.build()

# Stop and dispose of the node with SIGINT/CTRL+C
if __name__ == "__main__":
    try:
        node.run()
    finally:
        node.dispose()
