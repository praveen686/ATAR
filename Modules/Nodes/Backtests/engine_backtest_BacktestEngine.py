#!/usr/bin/env python3

# The copyright, license, and import statements remain the same...

from decimal import Decimal
import pandas as pd
import time

from nautilus_trader.backtest.engine import BacktestEngine, BacktestEngineConfig
from nautilus_trader.backtest.models import FillModel
from nautilus_trader.backtest.modules import FXRolloverInterestConfig, FXRolloverInterestModule
from nautilus_trader.config import BacktestDataConfig
from nautilus_trader.core.datetime import dt_to_unix_nanos
from nautilus_trader.data.engine import ParquetDataCatalog
from nautilus_trader.examples.strategies.ema_cross import EMACross, EMACrossConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data.tick import QuoteTick
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.model.objects import Money
from nautilus_trader.persistence.wranglers import QuoteTickDataWrangler
from nautilus_trader.test_kit.providers import TestDataProvider, TestInstrumentProvider

if __name__ == "__main__":
    engine = BacktestEngine(config=BacktestEngineConfig(trader_id="BACKTESTER-001"))

    # Firstly, add a trading venue (multiple venues possible)
    SIM =Venue("SIM")


    engine.add_venue(
        venue=SIM,
        oms_type=OmsType.HEDGING,  # Venue will generate position IDs
        account_type=AccountType.MARGIN,
        base_currency=USD,  # Standard single-currency account
        starting_balances=[Money(1_000_000, USD)],  # Single-currency or multi-currency accounts
        fill_model=FillModel(# Create a fill model (optional)
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
    start_time = dt_to_unix_nanos(pd.Timestamp('2021-01-05', tz='UTC'))
    end_time = dt_to_unix_nanos(pd.Timestamp('2021-01-06', tz='UTC'))
    catalog_path = "/home/ruben/PycharmProjects/Genie-Trader/Data/catalog"  # todo change to dynamic and/or buckets
    catalog = ParquetDataCatalog(catalog_path)

    # Add instruments
    AUDUSD_SIM = catalog.instruments(
        as_nautilus=True,
        instrument_ids=["AUDUSD.SIM"])[0]
    engine.add_instrument(AUDUSD_SIM)

    # Add data
    data = BacktestDataConfig(
        catalog_path=str(catalog.path),
        data_cls=QuoteTick,
        instrument_id=str(AUDUSD_SIM.id),
        end_time="2021-01-10",
    )
    print(type(data))
    wrangler = QuoteTickDataWrangler(instrument=AUDUSD_SIM)
    ticks = catalog.quote_ticks(start=start_time, end=end_time, instrument_ids=AUDUSD_SIM.id.value)

    ticks = wrangler.process(
        catalog.quote_ticks(start=start_time, end=end_time, instrument_ids=AUDUSD_SIM.id.value,as_nautilus=True)

    )

    engine.add_data(ticks)
    engine
    exit()

    engine.add_strategy(
        strategy=EMACross(
            config=EMACrossConfig(
                instrument_id=str(AUDUSD_SIM.id),
                bar_type="AUD/USD.SIM-1-MINUTE-MID-INTERNAL",
                fast_ema_period=10,
                slow_ema_period=20,
                trade_size=Decimal(1_000_000),
            )
        )
    )

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
