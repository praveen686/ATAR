import datetime
import os
import shutil
from decimal import Decimal

import fsspec
import pandas as pd
from nautilus_trader.core.datetime import dt_to_unix_nanos
from nautilus_trader.examples.algorithms.twap import TWAPExecAlgorithm
from nautilus_trader.examples.strategies.ema_cross_bracket_algo import EMACrossBracketAlgo, EMACrossBracketAlgoConfig
from nautilus_trader.model.data.tick import QuoteTick
from nautilus_trader.model.objects import Price, Quantity

from nautilus_trader.test_kit.providers import TestInstrumentProvider
from nautilus_trader.backtest.node import BacktestNode, BacktestVenueConfig, BacktestDataConfig, BacktestRunConfig, BacktestEngineConfig
from nautilus_trader.config import ImportableStrategyConfig
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.persistence.external.core import process_files, write_objects
from nautilus_trader.persistence.external.readers import TextReader

catalog_path = "/home/ruben/PycharmProjects/Genie-Trader/Data/catalog"  # todo change to dynamic and/or buckets
catalog = ParquetDataCatalog(catalog_path)

import pandas as pd
from nautilus_trader.core.datetime import dt_to_unix_nanos


start_time = dt_to_unix_nanos(pd.Timestamp('2021-01-05', tz='UTC'))
end_time =  dt_to_unix_nanos(pd.Timestamp('2021-01-05', tz='UTC'))

# catalog.quote_ticks(start=start, end=end)

instrument = catalog.instruments(as_nautilus=True)[0]

venues_config=[
    BacktestVenueConfig(
        name="SIM",
        oms_type="HEDGING",
        account_type="MARGIN",
        base_currency="USD",
        starting_balances=["1_000_000 USD"],
    )
]

data_config=[
    BacktestDataConfig(
        # catalog_path=str(ParquetDataCatalog.from_env().path),
        catalog_path=catalog_path,
        data_cls=QuoteTick,
        instrument_id=instrument.id.value,
        start_time=start_time,
        end_time=end_time,
    )
]

strategies = [
    ImportableStrategyConfig(
        strategy_path="nautilus_trader.examples.strategies.ema_cross:EMACross",
        config_path="nautilus_trader.examples.strategies.ema_cross:EMACrossConfig",
        config=dict(
            instrument_id=instrument.id.value,
            bar_type=f"{instrument.id.value}-15-MINUTE-BID-INTERNAL",
            # bar_type=f"{instrument.id.value}-15-SECOND-BID-INTERNAL",
            fast_ema_period=10,
            slow_ema_period=20,
            trade_size=Decimal(1_000_000),
        ),
    ),
]

config = BacktestRunConfig(
    engine=BacktestEngineConfig(strategies=strategies),
    data=data_config,
    venues=venues_config,
)

node = BacktestNode(configs=[config])


results = node.run()

with pd.option_context(
        "display.max_rows",
        100,
        "display.max_columns",
        None,
        "display.width",
        300,
):
    # print(engine.trader.generate_account_report(Venue("SIM")))
    # print(engine.trader.generate_order_fills_report())
    # print(engine.trader.generate_positions_report())

    for backtest in results:
        print(backtest.trader.generate_account_report(backtest.venues[0].name))
        print(backtest.trader.generate_order_fills_report())
        print(backtest.trader.generate_positions_report())

node.dispose()