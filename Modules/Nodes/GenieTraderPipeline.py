from os import environ

import pandas as pd
from nautilus_trader.adapters.binance.factories import BinanceLiveDataClientFactory, BinanceLiveExecClientFactory
from nautilus_trader.backtest.engine import BacktestEngine, Decimal, Environment, DataEngineConfig, RiskEngineConfig, \
    ExecEngineConfig
from nautilus_trader.backtest.engine import BacktestEngineConfig
from nautilus_trader.config import CacheDatabaseConfig, BacktestDataConfig, LiveRiskEngineConfig, LiveDataEngineConfig
from nautilus_trader.config import InstrumentProviderConfig
from nautilus_trader.config import LiveExecEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.core.datetime import dt_to_unix_nanos
from nautilus_trader.core.rust.model import OmsType, AccountType
from nautilus_trader.live.node import TradingNode
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import QuoteTick
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money

from Modules.Nodes.MarketVolatilityCatcher import MarketVolatilityCatcherConfig, MarketVolatilityCatcher, \
    TWAPExecAlgorithm


from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
from nautilus_trader.adapters.binance.config import BinanceDataClientConfig
from nautilus_trader.adapters.binance.config import BinanceExecClientConfig


def get_instruments_in_catalog(catalog_path, instrument_ids=None, as_nautilus=True, return_catalog=False):
    from nautilus_trader.persistence.catalog import ParquetDataCatalog
    catalog = ParquetDataCatalog(catalog_path)
    if instrument_ids is not None:
        instruments = catalog.instruments(as_nautilus=as_nautilus, instrument_ids=instrument_ids)
    else:
        instruments = catalog.instruments(as_nautilus=as_nautilus)

    if return_catalog:
        return instruments, catalog
    else:
        return instruments


class PipeLine:
    _defaults = None

    def configure_node(self):
        # Placeholder method for building the node
        pass

    def set_up_venue(self, **kwargs):
        # Placeholder method for setting up the venue
        pass

    def set_up_data(self, **kwargs):
        # Placeholder method for setting up data
        pass

    def set_up_execution_engine(self, **kwargs):
        # Placeholder method for setting up execution engine
        pass

    def run(self):
        # Placeholder method for running the node
        pass

    def print_reports(self):
        # Placeholder method for printing reports
        pass

    def get_value_from_kwargs(self, kwargs, key):
        return kwargs.get(key) or (getattr(self, key) or self._defaults.get(key, None))


class GenieBacktestNode(PipeLine):
    _defaults = dict(
        node_type="BACKTESTING",
        venue_name="SIM",
        oms_type=OmsType.HEDGING,
        account_type=AccountType.MARGIN,
        base_currency=USD,
        starting_balances=[Money(1_000_000, USD)],
        fill_model=None,
        modules=None,
        catalog_path=None,
        instrument_ids=None,
        start_time=None,
        end_time=None,
        data_config=None,
        strategy_config=None,
        exec_algorithm=TWAPExecAlgorithm(),
    )

    def __init__(self, **kwargs):

        self.node = None
        self.venue_name = kwargs.get("venue_name", None)
        self.oms_type = kwargs.get("oms_type", None)
        self.account_type = kwargs.get("account_type", None)
        self.base_currency = kwargs.get("base_currency", None)
        self.starting_balances = kwargs.get("starting_balances", None)
        self.fill_model = kwargs.get("fill_model", None)
        self.modules = kwargs.get("modules", None)
        self.catalog_path = kwargs.get("catalog_path", None)
        self.instrument_ids = kwargs.get("instrument_ids", None)
        self.start_time = kwargs.get("start_time", None)
        self.end_time = kwargs.get("end_time", None)
        self.data_config = kwargs.get("data_config", None)
        self.strategy_config = kwargs.get("strategy_config", None)
        self.exec_algorithm = kwargs.get("exec_algorithm", None)

    def configure_node(self, backtest_engine_config=None):
        if backtest_engine_config is None:
            backtest_engine_config = BacktestEngineConfig(
                environment=Environment.BACKTEST,
                trader_id='BACKTESTER-001',
                instance_id=None,
                cache=None,
                cache_database=None,
                data_engine=DataEngineConfig(
                    time_bars_build_with_no_updates=True,
                    time_bars_timestamp_on_close=True,
                    validate_data_sequence=False,
                    debug=False
                ),
                risk_engine=RiskEngineConfig(
                    bypass=False,
                    max_order_submit_rate='100/00:00:01',
                    max_order_modify_rate='100/00:00:01',
                    max_notional_per_order={},
                    debug=False
                ),
                exec_engine=ExecEngineConfig(
                    load_cache=True,
                    allow_cash_positions=True,
                    debug=False
                ),
                streaming=None,
                catalog=None,
                actors=[],
                strategies=[],
                exec_algorithms=[],
                load_state=False,
                save_state=False,
                loop_debug=False,
                logging=None,
                timeout_connection=10.0,
                timeout_reconciliation=10.0,
                timeout_portfolio=10.0,
                timeout_disconnection=10.0,
                timeout_post_stop=10.0,
                run_analysis=True
            )

        '''Build Node'''
        self.node = BacktestEngine(config=backtest_engine_config)

    def set_up_venue(self, **kwargs):
        assert self.node is not None, "Node must be built first"

        sim_venue = Venue(
            self.get_value_from_kwargs(kwargs, "venue_name"))  # Add a trading venue (multiple venues possible)
        oms_type = self.get_value_from_kwargs(kwargs, "oms_type")  # Venue will generate position IDs
        account_type = self.get_value_from_kwargs(kwargs, "account_type")  # Account type
        base_currency = self.get_value_from_kwargs(kwargs, "base_currency")  # Standard single-currency account
        starting_balances = self.get_value_from_kwargs(kwargs, "starting_balances")  # Starting balances

        # Create a fill model (optional), otherwise default is used or can be set based on venue
        # FillModel(prob_fill_on_limit=0.2, prob_fill_on_stop=0.95, prob_slippage=0.5, random_seed=42)
        fill_model = self.get_value_from_kwargs(kwargs, "fill_model")
        # There are many modules that can be added to the venue (optional) some require data to be passed
        # [ FXRolloverInterestModule(config=FXRolloverInterestConfig(short - term - interest.csv))]
        modules = self.get_value_from_kwargs(kwargs, "modules")

        self.node.add_venue(
            # venue ( Venue ) – The venue ID.
            venue=sim_venue,
            # oms_type (OmsType { HEDGING , NETTING }) – The order management system type for the exchange. If HEDGING will generate new position IDs.
            oms_type=oms_type,
            # account_type ( AccountType ) – The account type for the client.
            account_type=account_type,
            # starting_balances ( list [ Money ] ) – The starting account balances (specify one for a single asset account).
            starting_balances=starting_balances,
            # base_currency ( Currency , optional ) – The account base currency for the client. Use None for multi-currency accounts.
            base_currency=base_currency,
            # default_leverage ( Decimal , optional ) – The account default leverage (for margin accounts).
            default_leverage=None,
            # leverages ( dict [ InstrumentId , Decimal ] , optional ) – The instrument specific leverage configuration (for margin accounts).
            leverages=None,
            # modules ( list [ SimulationModule ] , optional ) – The simulation modules to load into the exchange.
            modules=modules,
            # fill_model ( FillModel , optional ) – The fill model for the exchange.
            fill_model=fill_model,
            # latency_model ( LatencyModel , optional ) – The latency model for the exchange.
            latency_model=None,
            # book_type (BookType, default BookType.L1_TBBO ) – The default order book type for fill modelling.
            # book_type=BookType.L1_TBBO,
            # routing ( bool , default False ) – If multi-venue routing should be enabled for the execution client.
            routing=False,
            # frozen_account ( bool , default False ) – If the account for this exchange is frozen (balances will not change).
            frozen_account=False,
            # bar_execution ( bool , default True ) – If bars should be processed by the matching engine(s) (and move the market).
            bar_execution=True,
            # reject_stop_orders ( bool , default True ) – If stop orders are rejected on submission if trigger price is in the market.
            reject_stop_orders=True,
            # support_gtd_orders ( bool , default True ) – If orders with GTD time in force will be supported by the venue.
            support_gtd_orders=True,
            # use_random_ids ( bool , default False ) – If venue order and position IDs will be randomly generated UUID4s.
            use_random_ids=False,
        )

    def set_up_data(self, instruments_config, **kwargs):
        catalog_path = self.get_value_from_kwargs(kwargs, "catalog_path")
        # instrument_ids = self.get_value_from_kwargs(kwargs, "instrument_ids")
        start_time = self.get_value_from_kwargs(kwargs, "start_time")
        end_time = self.get_value_from_kwargs(kwargs, "end_time")
        #
        assert catalog_path is not None, "Catalog path must be provided"
        instruments_ids = list(instruments_config.keys())
        assert instruments_ids is not None, "Instrument IDs must be provided"

        from nautilus_trader.data.engine import ParquetDataCatalog
        catalog = ParquetDataCatalog(catalog_path)
        instruments = catalog.instruments(as_nautilus=True, instrument_ids=instruments_ids) \
            if instruments_ids is not None else catalog.instruments(as_nautilus=True)

        if len(instruments) == 0:
            print("No selected instruments found in catalog")
            exit()

        if len(instruments) != len(instruments_ids):
            print("Instruments not found in catalog:")
            print(set(instruments_ids) - set([instrument.id.value for instrument in instruments]))

        # Lets assure all instruments required are added to the catalog and contain the required data based on the
        # start and end time provided

        print(instruments)
        exit()
        #
        for instrument, trade_size, bar_type in instruments_config.values():
            # assert instruments in instrument_ids, f"{instrument} not in {instrument_ids}"
            # Add instruments
            self.node.add_instrument(instrument)  # adds an instrument to engine and venue and cache

            data_config = BacktestDataConfig(  # TODO: this can be a list of BacktestDataConfigs instead of just one
                catalog_path=catalog_path,
                data_cls=QuoteTick,
                # instrument_id=str(instrument.id),
                instrument_id=instrument,
                start_time=dt_to_unix_nanos(start_time),
                end_time=dt_to_unix_nanos(end_time),
            )

            # # TODO refactor to handle ImportableStrategyConfig
            # Configure your strategy
            strategy_config = MarketVolatilityCatcherConfig(
                strategy_id=instrument,
                instrument_id=instrument,
                external_order_claims=[instrument],
                bar_type=f"{instrument}-{bar_type}",
                atr_period=7,
                atr_multiple=0.5,
                trade_size=trade_size,
            )

            # VolatilityMarketMaker(config=VolatilityMarketMakerConfig(
            #     strategy_id=instrument.id.value,
            #     instrument_id=instrument.id.value,
            #     external_order_claims=[instrument.id.value],
            #     bar_type=f"{instrument.id.value}-5-TICK-LAST-INTERNAL",
            #     atr_period=7,
            #     atr_multiple=0.5,
            #     trade_size=Decimal('0.01'),
            # )
            # )

            # TODO: refactor to handle multiple strategies. To be fair this has to be done for the entire BT-pipeline
            # strategy_config = ImportableStrategyConfig(
            # strategy_path="nautilus_trader.examples.strategies.ema_cross_bracket_algo:EMACrossBracketAlgo",
            # config_path="nautilus_trader.examples.strategies.ema_cross_bracket_algo:EMACrossBracketAlgoConfig",
            # config=dict(
            # instrument_id=instrument.id.value,
            # # bar_type=f"{instrument.id.value}-1-SECOND-BID-INTERNAL",
            # bar_type=f"{instrument.id.value}-30-MINUTE-BID-INTERNAL",
            # # bar_type=f"{instrument.id.value}-5-TICK-LAST-INTERNAL",
            # # bar_type=f"{backtest_interface.instruments[0].id.value}-1-DAY-BID-INTERNAL",
            # trade_size=Decimal(100_000),
            # atr_period=14,
            # fast_ema_period=7,
            # slow_ema_period=14,
            # bracket_distance_atr=1.8,
            # emulation_trigger="NO_TRIGGER",
            # manage_gtd_expiry=True,
            # entry_exec_algorithm_id=None,
            # entry_exec_algorithm_params=None,
            # sl_exec_algorithm_id=None,
            # sl_exec_algorithm_params=None,
            # tp_exec_algorithm_id=None,
            # tp_exec_algorithm_params=None,
            # close_positions_on_stop=True,
            # )
            # )

            # Add data
            data_loaded = data_config.load(as_nautilus=True)
            self.node.add_data(data_loaded["data"])

            # Add strategies
            self.node.add_strategy(MarketVolatilityCatcher(config=strategy_config))

    def set_up_execution_engine(self, **kwargs):

        exec_algorithm = kwargs.get("exec_algorithm", self.exec_algorithm or self._defaults["exec_algorithm"])

        # Add execution algorithm
        self.node.add_exec_algorithm(exec_algorithm)

    def run(self):
        # Stop and dispose of the node with SIGINT/CTRL+C
        try:
            self.node.run()
        finally:
            with pd.option_context(
                    "display.max_rows",
                    100,
                    "display.max_columns",
                    None,
                    "display.width",
                    300,
            ):

                print(self.node.trader.generate_account_report(Venue("SIM")))  # fixme hardcoded venue
                print(self.node.trader.generate_order_fills_report())
                print(self.node.trader.generate_positions_report())

            self.node.reset()
            self.node.dispose()


class GenieLiveNode(PipeLine):

    def __init__(self, **kwargs):
        self.node = None

        # Get Environmental Variables
        from Modules.Misc.misc import load_dot_env

        self.venue_name:str = kwargs.get('venue')
        self._use_simulated_venue = '-SIM' in self.venue_name.upper()
        self.venue_name = self.venue_name.removesuffix('-SIM')

        # Loads BINANCE_FUTURES_TESTNET_API_SECRET and BINANCE_FUTURES_TESTNET_API_KEY among other values
        load_dot_env(env_file="/.env")

    def configure_node(self, api_key=None, api_secret=None):
        """
        Environment contexts
            Backtest - Historical data with simulated venues
            Sandbox - Real-time data with simulated venues
            Live - Real-time data with live venues (paper trading or real accounts)
        """
        '''Fill Component Configurations'''

        from os import environ

        if self._use_simulated_venue:
            print(
                f'Using \"-SIM\" flag found in Venue Name as Naive Indication that you want to use _testnet thus '
                f'looking for {self.venue_name.upper()}_FUTURES_TESTNET_API_KEY')
            api_secret = api_secret or environ.get(f"{self.venue_name.upper()}_FUTURES_TESTNET_API_SECRET")
            api_key = api_key or environ.get(f"{self.venue_name.upper()}_FUTURES_TESTNET_API_KEY")
        else:
            api_key = api_key or environ.get(f"{self.venue_name.upper()}_API_KEY")
            api_secret = api_secret or environ.get(f"{self.venue_name.upper()}_API_SECRET")


        if not self.venue_name:
            return
        elif self.venue_name.upper() == 'BINANCE':
            # Data
            data_clients = {
                f"{self.venue_name.upper()}": BinanceDataClientConfig(
                    api_key=api_key,
                    api_secret=api_secret,
                    account_type=BinanceAccountType.USDT_FUTURE,
                    # account_type=MEXCAccountType.SPOT,
                    base_url_http=None,  # Override with custom endpoint
                    base_url_ws=None,  # Override with custom endpoint
                    us=True,  # If client is for Binance US
                    testnet=self._use_simulated_venue,  # If client uses the testnet
                    instrument_provider=InstrumentProviderConfig(load_all=True),
                ),
            }
            # Execution
            exec_clients = {
                f"{self.venue_name.upper()}": BinanceExecClientConfig(
                    api_key=api_key,
                    api_secret=api_secret,
                    # account_type=MEXCAccountType.SPOT,
                    account_type=BinanceAccountType.USDT_FUTURE,
                    base_url_http=None,  # Override with custom endpoint
                    base_url_ws=None,  # Override with custom endpoint
                    us=False,  # If client is for Binance US
                    testnet=self._use_simulated_venue,  # If client uses the testnet
                    instrument_provider=InstrumentProviderConfig(load_all=True),
                ),
            }
        config_node = TradingNodeConfig(
            environment=Environment.LIVE,
            trader_id='TRADER-001',
            instance_id=None,
            cache=None,
            cache_database=CacheDatabaseConfig(type="in-memory"),
            # cache_database=CacheDatabaseConfig(type="redis", host="localhost", port=6378,flush_on_start=False),
            data_engine=LiveDataEngineConfig(
                time_bars_build_with_no_updates=True,
                time_bars_timestamp_on_close=True,
                validate_data_sequence=False,
                debug=False,
                qsize=10000
            ),
            risk_engine=LiveRiskEngineConfig(
                bypass=False,
                max_order_submit_rate='100/00:00:01',
                max_order_modify_rate='100/00:00:01',
                max_notional_per_order={},
                debug=False,
                qsize=10000
            ),
            exec_engine=LiveExecEngineConfig(
                load_cache=True,
                allow_cash_positions=True,
                debug=False,
                reconciliation=True,
                reconciliation_lookback_mins=None,
                inflight_check_interval_ms=2000,
                inflight_check_threshold_ms=5000,
                qsize=10000
            ),
            streaming=None,
            catalog=None,
            actors=[],
            strategies=[],
            exec_algorithms=[],
            load_state=False,
            save_state=False,
            loop_debug=False,
            logging=LoggingConfig(log_level="INFO"),
            timeout_connection=10.0,
            timeout_reconciliation=10.0,
            timeout_portfolio=10.0,
            timeout_disconnection=10.0,
            timeout_post_stop=10.0,
            data_clients=data_clients,
            exec_clients=exec_clients # fixme UNCOMMENT!!! only using data endpoints
        )

        '''Build Node'''
        self.node = TradingNode(config=config_node)

    def set_up_venue(self, **kwargs):
        assert self.node is not None, "Node must be built first"
        if not self.venue_name:
            return
        elif self.venue_name.upper() == 'BINANCE':
            # Register your client factories with the node (can take user defined factories)
            self.node.add_data_client_factory("BINANCE", BinanceLiveDataClientFactory)
            self.node.add_exec_client_factory("BINANCE", BinanceLiveExecClientFactory)
        elif self.venue_name.upper() == 'MEXC':
            # Register your client factories with the node (can take user defined factories)
            from Modules.Nodes.Integrations.mexc.factories import MEXCLiveDataClientFactory
            self.node.add_data_client_factory("MEXC", MEXCLiveDataClientFactory)
            from Modules.Nodes.Integrations.mexc.factories import MEXCLiveExecClientFactory
            self.node.add_exec_client_factory("MEXC", MEXCLiveExecClientFactory)

    def set_up_data(self, instruments_config, **kwargs):

        # Add your strategies to the node
        for instrument, trade_size, bar_type in instruments_config.values():
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

            # Add your strategies and modules
            self.node.trader.add_strategy(strategy)

    def set_up_execution_engine(self):
        exec_algorithm = TWAPExecAlgorithm()

        # Add execution algorithm
        # engine.add_exec_algorithm(exec_algorithm)
        self.node.trader.add_exec_algorithm(exec_algorithm)

    def run(self):
        try:
            self.node.build()
            # Stop and dispose of the node with SIGINT/CTRL+C

            self.node.run()
        except KeyboardInterrupt:
            with pd.option_context(
                    "display.max_rows",

                    100,
                    "display.max_columns",
                    None,
                    "display.width",
                    300,
            ):
                # TODO: This should not be hard coded and remember with engines this might be different
                if not self.venue_name:
                    return
                elif self.venue_name.upper() == 'BINANCE':
                    print(self.node.trader.generate_account_report(Venue("BINANCE")))
                elif self.venue_name.upper() == 'MEXC':
                    print(self.node.trader.generate_account_report(Venue("MEXC")))
                print(self.node.trader.generate_order_fills_report())
                print(self.node.trader.generate_positions_report())

            self.node.dispose()


def GenieTraderPipeline(node_type, **kwargs):  # Use this instead of directly instantiating the node
    if node_type == "TRADING":
        return GenieLiveNode(**kwargs)
    elif node_type == "BACKTESTING":
        return GenieBacktestNode(**kwargs)
    else:
        raise ValueError(f"Node type {node_type} is not supported")


# todo this is specific to binance or just the forex data i have currently locally, overlooking this since is not a
#  roadblock for anyone using this as an example to customumize


if __name__ == "__main__":
    from Modules.Misc.misc import load_dot_env

    # FIXME This is a very hard coded example, need to make it more flexible. The goal of this script is to work on the Genie Trader project

    START_TIME = pd.Timestamp("2021-01-07-00:00:00", tz="UTC")
    END_TIME = pd.Timestamp("2021-01-07-09:00:00", tz="UTC")
    CATALOG_PATH = "/home/ruben/PycharmProjects/Genie-Trader/Data/tick_data_catalog"
    # VENUE_NAME = "SIM"
    # NODE_TYPE = "BACKTESTING"
    VENUE_NAME = "BINANCE-SIM"
    # VENUE_NAME = "MEXC"
    NODE_TYPE = "TRADING"

    # Set Environment Variables
    # Loads BINANCE_FUTURES_TESTNET_API_SECRET and BINANCE_FUTURES_TESTNET_API_KEY among other values
    load_dot_env(env_file="/.env")

    # Kwargs can be passed to the pipeline at any point, they will be passed to the node that is being created
    # Either at initiation or at the corresponding run method for the called method
    pipe = GenieTraderPipeline(node_type=NODE_TYPE,
                               **dict(
                                   # TODO: '''Venue Settings'''
                                   venue=VENUE_NAME,
                                   oms_type=OmsType.HEDGING,
                                   account_type=AccountType.MARGIN,
                                   starting_balances=[Money(1_000_000, USD)],
                                   base_currency=USD,
                                   default_leverage=None,
                                   leverages=None,
                                   modules=None,
                                   fill_model=None,
                                   latency_model=None,
                                   # book_type=BookType.L1_TBBO,
                                   routing=False,
                                   frozen_account=False,
                                   bar_execution=True,
                                   reject_stop_orders=True,
                                   support_gtd_orders=True,
                                   use_random_ids=False,

                                   # TODO: '''Data Settings'''
                                   catalog_path=CATALOG_PATH,
                                   # instrument_ids=INSTRUMENT_IDS,
                                   start_time=START_TIME,
                                   end_time=END_TIME,
                               ))

    # FIXME this might return a node or an engine, need to check and make nessesary changes throughout the script to handle both cases for Live and Backtesting

    '''Create Node or Engine'''
    API_KEY = environ.get("BINANCE_FUTURES_TESTNET_API_KEY")
    API_SECRET = environ.get("BINANCE_FUTURES_TESTNET_API_SECRET")
    pipe.configure_node(API_KEY, API_SECRET)
    '''Venue Config'''
    pipe.set_up_venue()
    '''Instruments and Data Selection '''
    # TODO: should be able to use live data in paper trading, should be able to download data or use the catalog
    #  data or of course download and insert data
    #  in catalog
    pipe.set_up_data(
        instruments_config=dict(
            # Instruments to trade
            BTCUSDT_PERP_MEXC=[f"BTCUSDT-PERP.{VENUE_NAME.upper().removesuffix('-SIM')}", Decimal(str(0.001 * 5)), "1-MINUTE-LAST-EXTERNAL"],
            # BTCUSDT_PERP_BINANCE=[f"BTCUSDT-PERP.{VENUE_NAME.upper()}", Decimal(str(0.001 * 5)), "1-MINUTE-LAST-EXTERNAL"],
            # ETHUSDT_PERP_BINANCE=["ETHUSDT-PERP.BINANCE", Decimal(str(0.003 * 10)), "1-MINUTE-LAST-EXTERNAL"],
            # BCHUSDT_PERP_BINANCE=["BCHUSDT-PERP.BINANCE", Decimal(str(0.053 * 6)), "1-MINUTE-LAST-EXTERNAL"],
            # LTCUSDT_PERP_BINANCE=["LTCUSDT-PERP.BINANCE", Decimal(str(0.068 * 6)), "1-MINUTE-LAST-EXTERNAL"],
            #
            # BTCUSDT_PERP_BINANCE=["BTCUSDT-PERP.BINANCE", Decimal(str(0.001 * 5)), "1-SECOND-MID-INTERNAL"],
            # ETHUSDT_PERP_BINANCE=["ETHUSDT-PERP.BINANCE", Decimal(str(0.003 * 10)), "1-SECOND-MID-INTERNAL"],
            # BCHUSDT_PERP_BINANCE=["BCHUSDT-PERP.BINANCE", Decimal(str(0.053 * 6)), "1-SECOND-MID-INTERNAL"],
            # LTCUSDT_PERP_BINANCE=["LTCUSDT-PERP.BINANCE", Decimal(str(0.068 * 6)), "1-SECOND-MID-INTERNAL"],
        ))

    "Configure your execution algorithm"
    pipe.set_up_execution_engine()

    """Run Node"""  # TODO: please remember we still need to figure out the node vs engine handling and abilities
    pipe.run()

    #######################################################################################################################
    ## Everything below this line is scratch or no place in the script right now
    #######################################################################################################################
    # TODO: Implement Backtesting using backtest node rather than just engine  (see below)
    #   elif node_type == "GRID_BACKTESTING":
    #   Implement grid backtesting
    #   "Engine Config"
    #   from nautilus_trader.config import BacktestRunConfig
    #   engine_config = BacktestRunConfig(
    #     engine=BacktestEngineConfig(strategies=strategies), #idk if only accepts config or can accept engine
    #     data=data_config,
    #     venues=venues_config,
    #   )
    #  engine = BacktestEngine(config=BacktestEngineConfig(strategies=strategies))
    #  engine.add_data(data_config)
    #  engine.add_venue(venues_config)
    #  "Set up Node"
    #  node = BacktestNode(configs=[engine_config])
