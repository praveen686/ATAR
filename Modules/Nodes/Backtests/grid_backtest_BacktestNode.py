from decimal import Decimal

import pandas as pd
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.node import BacktestNode, BacktestVenueConfig, BacktestDataConfig, BacktestRunConfig, \
    BacktestEngineConfig
from nautilus_trader.backtest.results import BacktestResult
from nautilus_trader.config import ImportableStrategyConfig
from nautilus_trader.core.datetime import dt_to_unix_nanos
from nautilus_trader.model.data.tick import QuoteTick
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.persistence.catalog import ParquetDataCatalog

"Catalog Load"
catalog_path = "/home/ruben/PycharmProjects/Genie-Trader/Data/catalog"  # todo change to buckets
catalog = ParquetDataCatalog(catalog_path)

"SET-UP"
start_time = dt_to_unix_nanos(pd.Timestamp('2021-01-05', tz='UTC'))
end_time = dt_to_unix_nanos(pd.Timestamp('2021-01-06', tz='UTC'))
instrument = catalog.instruments(as_nautilus=True)[0]
instrument1 = catalog.instruments(as_nautilus=True)[1]

"Venue Config"
venues_config = [
    BacktestVenueConfig(
        name="SIM",
        oms_type="HEDGING",
        account_type="MARGIN",
        base_currency="USD",
        starting_balances=["1_000_000 USD"],
    )
]

"Data Config"
data_config = [
    BacktestDataConfig(
        # catalog_path=str(ParquetDataCatalog.from_env().path),
        catalog_path=catalog_path,
        data_cls=QuoteTick,
        instrument_id=instrument.id.value,
        start_time=start_time,
        end_time=end_time,
    ),
    BacktestDataConfig(
        # catalog_path=str(ParquetDataCatalog.from_env().path),
        catalog_path=catalog_path,
        data_cls=QuoteTick,
        instrument_id=instrument1.id.value,
        start_time=start_time,
        end_time=end_time,
    )
]

"Strategy Config"
strategies = [

    ImportableStrategyConfig(
        strategy_path="nautilus_trader.examples.strategies.ema_cross_bracket_algo:EMACrossBracketAlgo",
        config_path="nautilus_trader.examples.strategies.ema_cross_bracket_algo:EMACrossBracketAlgoConfig",
        config=dict(
            instrument_id=instrument.id.value,
            # bar_type=f"{backtest_interface.instruments[0].id.value}-15-SECOND-BID-INTERNAL",
            bar_type=f"{instrument.id.value}-1-HOUR-BID-INTERNAL",
            # bar_type=f"{backtest_interface.instruments[0].id.value}-1-DAY-BID-INTERNAL",
            trade_size=Decimal(100_000),
            atr_period=14,
            fast_ema_period=7,
            slow_ema_period=14,
            bracket_distance_atr=1.8,
            emulation_trigger="NO_TRIGGER",
            manage_gtd_expiry=True,
            entry_exec_algorithm_id=None,
            entry_exec_algorithm_params=None,
            sl_exec_algorithm_id=None,
            sl_exec_algorithm_params=None,
            tp_exec_algorithm_id=None,
            tp_exec_algorithm_params=None,
            close_positions_on_stop=True,
        )
    ),
    ImportableStrategyConfig(
        strategy_path="nautilus_trader.examples.strategies.ema_cross:EMACross",
        config_path="nautilus_trader.examples.strategies.ema_cross:EMACrossConfig",
        config=dict(
            instrument_id=instrument1.id.value,
            # bar_type=f"{instrument.id.value}-1-MINUTE-BID-INTERNAL",
            # bar_type=f"{instrument.id.value}-15-SECOND-BID-INTERNAL",
            bar_type=f"{instrument1.id.value}-1-HOUR-BID-INTERNAL",
            fast_ema_period=10,
            slow_ema_period=20,
            trade_size=Decimal(1_000_000),
        ),
    ),

]

"Engine Config"
engine_config = BacktestRunConfig(
    engine=BacktestEngineConfig(strategies=strategies),
    data=data_config,
    venues=venues_config,
)

# engine = BacktestEngine(config=BacktestEngineConfig(strategies=strategies))
#
# engine.add_data(data_config)
# engine.add_venue(venues_config)


"Set up Node"
node = BacktestNode(configs=[engine_config])

"Run Node"
results: list[BacktestResult] = node.run()

"Get Results"
print(results)

engine: BacktestEngine = node.get_engine(engine_config.id)

pd.option_context(
    "display.max_rows",
    100,
    "display.max_columns",
    None,
    "display.width",
    300,
)
# print(engine.trader.generate_order_fills_report())
# print(engine.trader.generate_positions_report())
# print(engine.trader.generate_account_report(Venue("SIM")))

orders_report = engine.trader.generate_orders_report()
order_fills_report = engine.trader.generate_order_fills_report()
positions_report = engine.trader.generate_positions_report()
account_report = engine.trader.generate_account_report(Venue("SIM"))

stats_pnl_formatted = engine.portfolio.analyzer.get_performance_stats_general()

print(orders_report)
print(order_fills_report)
print(positions_report)
print(account_report)
print(stats_pnl_formatted)

"Create Plots"
# todo most likely something like plotly plots


"Dispose Node"
node.dispose()
