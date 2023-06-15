#!/usr/bin/env python3
# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2023 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------

from decimal import Decimal

from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
from nautilus_trader.adapters.binance.config import BinanceDataClientConfig
from nautilus_trader.adapters.binance.config import BinanceExecClientConfig
from nautilus_trader.adapters.binance.factories import BinanceLiveDataClientFactory
from nautilus_trader.adapters.binance.factories import BinanceLiveExecClientFactory
from nautilus_trader.config import CacheDatabaseConfig
from nautilus_trader.config import InstrumentProviderConfig
from nautilus_trader.config import LiveExecEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.examples.algorithms.twap import TWAPExecAlgorithm
from nautilus_trader.examples.strategies.ema_cross_bracket_algo import EMACrossBracketAlgo
from nautilus_trader.examples.strategies.ema_cross_bracket_algo import EMACrossBracketAlgoConfig
from nautilus_trader.live.node import TradingNode


# *** THIS IS A TEST STRATEGY WITH NO ALPHA ADVANTAGE WHATSOEVER. ***
# *** IT IS NOT INTENDED TO BE USED TO TRADE LIVE WITH REAL MONEY. ***

# *** THIS INTEGRATION IS STILL UNDER CONSTRUCTION. ***
# *** CONSIDER IT TO BE IN AN UNSTABLE BETA PHASE AND EXERCISE CAUTION. ***

BINANCE_TESTNET_API_KEY="316ee06e009b0ec07b92d15328bed7f0a92c7e1ddb2ce8a755273a6d4f91c802"
BINANCE_TESTNET_API_SECRET="e56b5fbc30dee0b4eb951933b39bc6eb4864a7ae2b60768a6697960b3ff5e838"
# Configure the trading node
config_node = TradingNodeConfig(
    trader_id="TESTER-001",
    logging=LoggingConfig(log_level="INFO"),
    exec_engine=LiveExecEngineConfig(
        reconciliation=True,
        reconciliation_lookback_mins=1440,
    ),
    cache_database=CacheDatabaseConfig(type="in-memory"),
    data_clients={
        "BINANCE": BinanceDataClientConfig(
            api_key=BINANCE_TESTNET_API_KEY,  # "YOUR_BINANCE_TESTNET_API_KEY"
            api_secret=BINANCE_TESTNET_API_SECRET,  # "YOUR_BINANCE_TESTNET_API_SECRET"
            account_type=BinanceAccountType.FUTURES_USDT,
            base_url_http=None,  # Override with custom endpoint
            base_url_ws=None,  # Override with custom endpoint
            us=False,  # If client is for Binance US
            testnet=True,  # If client uses the testnet
            instrument_provider=InstrumentProviderConfig(load_all=True),
        ),
    },
    exec_clients={
        "BINANCE": BinanceExecClientConfig(
            api_key=BINANCE_TESTNET_API_KEY,  # "YOUR_BINANCE_TESTNET_API_KEY"
            api_secret=BINANCE_TESTNET_API_SECRET,  # "YOUR_BINANCE_TESTNET_API_SECRET"
            account_type=BinanceAccountType.FUTURES_USDT,
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
    timeout_post_stop=3.0,
)
# Instantiate the node with a configuration
node = TradingNode(config=config_node)




# Symbols to Trade (we are doing multiple instead of just one per exec_algorythm)
symbols_to_trade = [
    "ETHUSDT-PERP",
    "BTCUSDT-PERP",
    # "ADAUSDT-PERP",
    # "XRPUSDT-PERP",
    # "SOLUSDT-PERP",
]

# Configure your strategy
for symbol in symbols_to_trade:
    strat_config = EMACrossBracketAlgoConfig(
        order_id_tag=f"00{symbols_to_trade.index(symbol)}",
        instrument_id=f"{symbol}.BINANCE",
        external_order_claims=[f"{symbol}.BINANCE"],
        bar_type=f"{symbol}.BINANCE-1-MINUTE-LAST-EXTERNAL",
        # bar_type="ETHUSDT.BINANCE-1-TICK-LAST-EXTERNAL",
        fast_ema_period=7,
        slow_ema_period=14,
        bracket_distance_atr=0.3,
        trade_size=Decimal("0.05"),
        emulation_trigger="BID_ASK",
        entry_exec_algorithm_id="TWAP",
        entry_exec_algorithm_params={"horizon_secs": 10.0, "interval_secs": 2.5},
    )
    # Instantiate your strategy and Add your strategy
    strategy = EMACrossBracketAlgo(config=strat_config)
    node.trader.add_strategy(strategy)



# Add your execution algorithm and modules
exec_algorithm = TWAPExecAlgorithm()
node.trader.add_exec_algorithm(exec_algorithm)
#


# Register your client factories with the node (can take user defined factories)
node.add_data_client_factory("BINANCE", BinanceLiveDataClientFactory)
node.add_exec_client_factory("BINANCE", BinanceLiveExecClientFactory)
node.build()


# Stop and dispose of the node with SIGINT/CTRL+C
if __name__ == "__main__":
    try:
        node.run()
    finally:
        node.dispose()