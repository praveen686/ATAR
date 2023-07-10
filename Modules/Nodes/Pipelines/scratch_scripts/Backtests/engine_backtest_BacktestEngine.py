#!/usr/bin/env python3

# The copyright, license, and import statements remain the same...

import time
from decimal import Decimal

import pandas as pd
from nautilus_trader.backtest.engine import BacktestEngine, BacktestEngineConfig
from nautilus_trader.backtest.models import FillModel
from nautilus_trader.config import BacktestDataConfig
from nautilus_trader.core.datetime import dt_to_unix_nanos
from nautilus_trader.data.engine import ParquetDataCatalog
from nautilus_trader.examples.algorithms.twap import TWAPExecAlgorithm
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data.tick import QuoteTick
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money

from Modules.Nodes.examples.strategies.volatility_market_maker import VolatilityMarketMaker, VolatilityMarketMakerConfig

if __name__ == "__main__":
    engine = BacktestEngine(config=BacktestEngineConfig(trader_id="BACKTESTER-001"))

    # Firstly, add a trading venue (multiple venues possible)
    SIM = Venue("SIM")

    engine.add_venue(
        venue=SIM,
        oms_type=OmsType.HEDGING,  # Venue will generate position IDs
        account_type=AccountType.MARGIN,
        base_currency=USD,  # Standard single-currency account
        starting_balances=[Money(1_000_000, USD)],  # Single-currency or multi-currency accounts
        #
        fill_model=FillModel(  # Create a fill model (optional)
            prob_fill_on_limit=0.2,
            prob_fill_on_stop=0.95,
            prob_slippage=0.5,
            random_seed=42,
        ),
        # modules=[
        #     FXRolloverInterestModule(
        #         config=FXRolloverInterestConfig(
        #             # e.g short-term-interest.csv
        #             ...
        #         )
        #     )
        # ],
    )

    # Get Catalog
    NINSTRUMENTS = 1
    start_time = dt_to_unix_nanos(pd.Timestamp('2021-01-07', tz='UTC'))
    end_time = dt_to_unix_nanos(pd.Timestamp('2021-02-08', tz='UTC'))
    catalog_path = "/home/ruben/PycharmProjects/Genie-Trader/Data/tick_data_catalog"  # todo change to dynamic and/or buckets
    catalog = ParquetDataCatalog(catalog_path)
    instruments = catalog.instruments(as_nautilus=True)[NINSTRUMENTS]

    for instrument in instruments:
        # Add instruments
        engine.add_instrument(instrument)

        # Add data
        data = BacktestDataConfig(
            catalog_path=str(catalog.path),
            data_cls=QuoteTick,
            instrument_id=str(instrument.id),
            start_time=start_time,
            end_time=end_time,
        )
        data_loaded = data.load(as_nautilus=True)
        engine.add_data(data_loaded["data"])

        # Add strategies
        engine.add_strategy(
            VolatilityMarketMaker(config=VolatilityMarketMakerConfig(
                # strategy_id=f"{str(instrument.id)}-VolatilityMarketMaker",
                instrument_id=str(instrument.id),
                external_order_claims=[str(instrument.id)],
                bar_type=f"{instrument.id}-1-HOUR-MID-INTERNAL",
                atr_period=7,
                atr_multiple=0.5,
                trade_size=Decimal(1500),
            ))

        )

    # Configure your execution algorithm
    exec_algorithm = TWAPExecAlgorithm()

    # Add execution algorithm
    engine.add_exec_algorithm(exec_algorithm)
    time.sleep(0.1)

    # input("Press Enter to continue...")

    engine.run()

    with pd.option_context(
            "display.max_rows",
            100,
            "display.max_columns",
            None,
            "display.width",
            300,
    ):
        print(engine.trader.generate_account_report(Venue("SIM")))
        print(engine.trader.generate_order_fills_report())
        print(engine.trader.generate_positions_report())

    engine.reset()
    engine.dispose()
