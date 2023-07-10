import os

import pandas as pd
from nautilus_trader.core.rust.model import OmsType, AccountType, BookType
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.objects import Money

from Modules.Nodes.Pipelines.GenieTraderPipeline import GenieTraderPipeline

# todo this is specific to binance or just the forex data i have currently locally, overlooking this since is not a
#  roadblock for anyone using this as an example to customumize


if __name__ == "__main__":
    # FIXME This is a very hard coded example, need to make it more flexible. The goal of this script is to work on the Genie Trader project
    VENUE_NAME = "SIM"
    INSTRUMENT_IDS = ["AUDUSD.SIM"]
    START_TIME = pd.Timestamp("2021-01-07-00:00:00", tz="UTC")
    END_TIME = pd.Timestamp("2021-01-07-08:00:00", tz="UTC")
    CATALOG_PATH = "/home/ruben/PycharmProjects/Genie-Trader/Data/tick_data_catalog"
    NODE_TYPE = "BACKTESTING"
    # NODE_TYPE = "TRADING"
    # Set Environment Variables
    # read ../.env file and set environment variables
    with open("/home/ruben/PycharmProjects/Genie-Trader/Modules/Nodes/.env") as f:
        for line in f:
            key, value = line.strip().split("=")
            if key not in os.environ:
                print(f"Setting environment variable: {key}=****")
                os.environ[key] = value

    # Kwargs can be passed to the pipeline at any point, they will be passed to the node that is being created
    # Either at initiation or at the corresponding run method for the called method
    pipe = GenieTraderPipeline(node_type=NODE_TYPE,
                               **dict(
                                   # TODO: '''Venue Settings'''
                                   # venue ( Venue ) – The venue ID.
                                   venue=VENUE_NAME,
                                   # oms_type (OmsType { HEDGING , NETTING }) – The order management system type for the exchange. If HEDGING will generate new position IDs.
                                   oms_type=OmsType.HEDGING,
                                   # account_type ( AccountType ) – The account type for the client.
                                   account_type=AccountType.MARGIN,
                                   # starting_balances ( list [ Money ] ) – The starting account balances (specify one for a single asset account).
                                   starting_balances=[Money(1_000_000, USD)],
                                   # base_currency ( Currency , optional ) – The account base currency for the client. Use None for multi-currency accounts.
                                   base_currency=USD,
                                   # default_leverage ( Decimal , optional ) – The account default leverage (for margin accounts).
                                   default_leverage=None,
                                   # leverages ( dict [ InstrumentId , Decimal ] , optional ) – The instrument specific leverage configuration (for margin accounts).
                                   leverages=None,
                                   # modules ( list [ SimulationModule ] , optional ) – The simulation modules to load into the exchange.
                                   modules=None,
                                   # fill_model ( FillModel , optional ) – The fill model for the exchange.
                                   fill_model=None,
                                   # latency_model ( LatencyModel , optional ) – The latency model for the exchange.
                                   latency_model=None,
                                   # book_type (BookType, default BookType.L1_TBBO ) – The default order book type for fill modelling.
                                   book_type=BookType.L1_TBBO,
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
                                   #
                                   # TODO: '''Data Settings'''
                                   catalog_path=CATALOG_PATH,
                                   instrument_ids=INSTRUMENT_IDS,
                                   start_time=START_TIME,
                                   end_time=END_TIME,
                                   #
                               ))
    # FIXME this might return a node or an engine, need to check and make nessesary changes throughout the script to handle both cases for Live and Backtesting

    '''Create Node or Engine'''
    pipe.configure_node()
    '''Venue Config'''
    pipe.set_up_venue()
    '''Instruments and Data Selection '''
    # TODO: should be able to use live data in paper trading, should be able to download data or use the catalog
    #  data or of course download and insert data
    #  in catalog
    pipe.set_up_data()
    "Configure your execution algorithm"
    # pipe.set_up_execution_engine()

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
