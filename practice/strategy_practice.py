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
import nautilus_trader as genie_trader
from decimal import Decimal
from typing import Optional

import numpy as np
from nautilus_trader.common.enums import LogColor
from nautilus_trader.config import StrategyConfig
from nautilus_trader.core.data import Data
from nautilus_trader.core.message import Event
from nautilus_trader.indicators.atr import AverageTrueRange
from nautilus_trader.indicators.average.ema import ExponentialMovingAverage
from nautilus_trader.model.data.bar import Bar
from nautilus_trader.model.data.bar import BarType
from nautilus_trader.model.data.tick import QuoteTick
from nautilus_trader.model.data.tick import TradeTick
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TrailingOffsetType
from nautilus_trader.model.enums import TriggerType
from nautilus_trader.model.events.order import OrderFilled
from nautilus_trader.model.events.position import PositionChanged
from nautilus_trader.model.events.position import PositionClosed
from nautilus_trader.model.events.position import PositionOpened
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments.base import Instrument
from nautilus_trader.model.orderbook.book import OrderBook
from nautilus_trader.model.orders.market import MarketOrder
from nautilus_trader.model.orders.trailing_stop_market import TrailingStopMarketOrder
from nautilus_trader.trading.strategy import Strategy

import ccxt
# import vectorbtpro as vbt
# from TV_Binance.Binance_Orders_Handler import Binance_Orders_Handler
from nautilus_trader.model.objects import Price


# *** THIS IS A TEST STRATEGY WITH NO ALPHA ADVANTAGE WHATSOEVER. ***
# *** IT IS NOT INTENDED TO BE USED TO TRADE LIVE WITH REAL MONEY. ***


class Practice_Strat_Config(StrategyConfig):
    """
    Configuration for ``EMACrossTrailingStop`` instances.

    Parameters
    ----------
    instrument_id : InstrumentId
        The instrument ID for the strategy.
    bar_type : BarType
        The bar type for the strategy.
    atr_period : int
        The period for the ATR indicator.
    trailing_atr_multiple : float
        The ATR multiple for the trailing stop.
    trailing_offset_type : str
        The trailing offset type (interpreted as `TrailingOffsetType`).
    trigger_type : str
        The trailing stop trigger type (interpreted as `TriggerType`).
    trade_size : str
        The position size per trade (interpreted as Decimal).
    fast_ema_period : int, default 10
        The fast EMA period.
    slow_ema_period : int, default 20
        The slow EMA period.
    emulation_trigger : str, default 'NO_TRIGGER'
        The emulation trigger for submitting emulated orders.
        If 'NONE' then orders will not be emulated.
    order_id_tag : str
        The unique order ID tag for the strategy. Must be unique
        amongst all running strategies for a particular trader ID.
    oms_type : OmsType
        The order management system type for the strategy. This will determine
        how the `ExecutionEngine` handles position IDs (see docs).
    """

    instrument_id: str
    bar_type: str
    atr_period: int
    trailing_atr_multiple: float
    trailing_offset_type: str
    trigger_type: str
    trade_size: Decimal
    fast_ema_period: int = 10
    slow_ema_period: int = 20
    emulation_trigger: str = "NO_TRIGGER"

    #
    activation_percentage: float = 0.001


class Practice_Strat(Strategy):
    """
    A simple moving average cross example strategy with a stop-market entry and
    trailing stop.

    When the fast EMA crosses the slow EMA then submits a stop-market order one
    tick above the current bar for BUY, or one tick below the current bar
    for SELL.

    If the entry order is filled then a trailing stop at a specified ATR
    distance is submitted and managed.

    Cancels all orders and closes all positions on stop.

    Parameters
    ----------
    config : EMACrossTrailingStopConfig
        The configuration for the instance.
    """

    def __init__(self, config: Practice_Strat_Config):
        super().__init__(config)

        # Configuration
        self.instrument_id = InstrumentId.from_str(config.instrument_id)
        self.bar_type = BarType.from_str(config.bar_type)
        self.trade_size = Decimal(config.trade_size)
        self.trailing_atr_multiple = config.trailing_atr_multiple
        self.trailing_offset_type = TrailingOffsetType[config.trailing_offset_type]
        self.trigger_type = TriggerType[config.trigger_type]
        self.emulation_trigger = TriggerType[config.emulation_trigger]

        # Create the indicators for the strategy
        self.fast_ema = ExponentialMovingAverage(config.fast_ema_period)
        self.slow_ema = ExponentialMovingAverage(config.slow_ema_period)
        self.atr = AverageTrueRange(config.atr_period)

        self.instrument: Optional[Instrument] = None  # Initialized in on_start
        self.tick_size = None  # Initialized in on_start

        # Users order management variables
        self.entry = None
        self.trailing_stop = None
        self.position_id = None

        self.activation_percentage = config.activation_percentage

        # # Users redis variables
        # self.r = None
        # self.pubsub = None

        # Users binance variables

    def on_start(self):
        """Actions to be performed on strategy start."""
        self.instrument = self.cache.instrument(self.instrument_id)
        if self.instrument is None:
            self.log.error(f"Could not find instrument for {self.instrument_id}")
            self.stop()
            return

        self.tick_size = self.instrument.price_increment

        # Register the indicators for updating
        self.register_indicator_for_bars(self.bar_type, self.fast_ema)
        self.register_indicator_for_bars(self.bar_type, self.slow_ema)
        self.register_indicator_for_bars(self.bar_type, self.atr)

        # Get historical data
        self.request_bars(self.bar_type)

        # Subscribe to live data
        self.subscribe_bars(self.bar_type)
        self.subscribe_quote_ticks(self.instrument_id)

        self.hit = False
        # import redis
        # self.r = redis.from_url(
        #     url="redis://localhost:6379/0",
        #     decode_responses=True,
        # )
        # self.pubsub = self.r.pubsub()
        # self.pubsub.subscribe("tradingview_webhook_publisher")
        # for message in pubsub.listen():

    def on_stop(self):
        """
        Actions to be performed when the strategy is stopped.
        """
        self.cancel_all_orders(self.instrument_id)
        self.close_all_positions(self.instrument_id)

        # Unsubscribe from data
        self.unsubscribe_quote_ticks(self.instrument_id)
        self.unsubscribe_bars(self.bar_type)

    def on_reset(self):
        """
        Actions to be performed when the strategy is reset.
        """
        # Reset indicators here
        self.fast_ema.reset()
        self.slow_ema.reset()
        self.atr.reset()

    def on_instrument(self, instrument: Instrument):
        """
        Actions to be performed when the strategy is running and receives an
        instrument.

        Parameters
        ----------
        instrument : Instrument
            The instrument received.

        """
        self.log.info(f"on_instrument Received {instrument = }")

    def on_order_book(self, order_book: OrderBook):
        """
        Actions to be performed when the strategy is running and receives an order book.

        Parameters
        ----------
        order_book : OrderBook
            The order book received.

        """
        self.log.info(f"on_order_book Received {order_book = }")  # For debugging (must add a subscription)

    def on_quote_tick(self, tick: QuoteTick):
        """
        Actions to be performed when the strategy is running and receives a quote tick.

        Parameters
        ----------
        tick : QuoteTick
            The tick received.

        """
        self.log.info(f"on_quote_tick Received {repr(tick)}")

        if not self.hit:  # fixme delete lol
            if self.portfolio.is_flat(self.instrument_id):  # todo fix this
                # BUY LOGIC
                if self.fast_ema.value >= self.slow_ema.value:
                    self.entry_buy()
                # SELL LOGIC
                else:  # fast_ema.value < self.slow_ema.value
                    self.entry_sell()
                self.hit = True

        # message = self.pubsub.get_message(ignore_subscribe_messages=True)
        #
        # if message:
        #     message= message.decode("utf-8")
        # self.log.info(f"on_quote_tick Message Received {repr(message) = }")

    def on_trade_tick(self, tick: TradeTick):
        """
        Actions to be performed when the strategy is running and receives a trade tick.

        Parameters
        ----------
        tick : TradeTick
            The tick received.

        """
        self.log.info(f" on_trade_tick Received {repr(tick)}")

    def on_bar(self, bar: Bar):
        """
        Actions to be performed when the strategy is running and receives a bar.

        Parameters
        ----------
        bar : Bar
            The bar received.

        """
        self.log.info(f"on_bar Received {repr(bar)}")

        # Check if indicators ready
        if not self.indicators_initialized():
            self.log.info(
                f"Waiting for indicators to warm up " f"[{self.cache.bar_count(self.bar_type)}]...",
                color=LogColor.BLUE,
            )
            return  # Wait for indicators to warm up...

        if self.portfolio.is_flat(self.instrument_id):
            # BUY LOGIC
            if self.fast_ema.value >= self.slow_ema.value:
                self.entry_buy()
            # SELL LOGIC
            else:  # fast_ema.value < self.slow_ema.value
                self.entry_sell()

    def on_data(self, data: Data):
        """
        Actions to be performed when the strategy is running and receives generic data.

        Parameters
        ----------
        data : Data
            The data received.

        """
        self.log.info(f"on_data Received {repr(data)}")

    def on_event(self, event: Event):
        """
        Actions to be performed when the strategy is running and receives an event.

        Parameters
        ----------
        event : Event
            The event received.

        """

        self.log.info(f"on_event Received {repr(event)}")
        self.log.info(f"{type(event) = }")
        self.log.info(f"{event = }")

        if isinstance(event, OrderFilled):
            self.log.info(f"OrderFilled")
            if self.trailing_stop:
                self.log.info(f"self.trailing_stop")
                if event.client_order_id == self.trailing_stop.client_order_id:
                    self.log.info(f"event.client_order_id == self.trailing_stop.client_order_id")
                    self.trailing_stop = None
        elif isinstance(event, (PositionOpened, PositionChanged)):
            # PositionOpened(instrument_id=BTCUSDT - PERP.BINANCE, position_id=BTCUSDT - PERP.BINANCE - BOTH,
            #                account_id=BINANCE - futures - master, opening_order_id=O - 20230212 - 001 - 000 - 1,
            #                closing_order_id=None, entry=SELL, side=SHORT, net_qty=-0.001, quantity=0.001,
            #                peak_qty=0.001, currency=USDT, avg_px_open=21780.0, avg_px_close=0.0,
            #                realized_return=0.00000, realized_pnl=0.00000000
            # USDT, unrealized_pnl = 0.00000000
            # USDT, ts_opened = 1676239560767000064, ts_last = 1676239560767000064, ts_closed = 0, duration_ns = 0).

            self.log.info(f"PositionOpened or PositionChanged")
            if self.entry:
                self.log.info(f"self.entry")
                if event.opening_order_id == self.entry.client_order_id:
                    if event.entry == OrderSide.BUY:
                        self.position_id = event.position_id
                        # self.trailing_stop_sell(event)
                        self.add_trailing_stop(event)

                    elif event.entry == OrderSide.SELL:
                        self.position_id = event.position_id
                        # self.trailing_stop_buy(event)
                        self.add_trailing_stop(event)
        elif isinstance(event, PositionClosed):
            self.log.info(f"PositionClosed")
            self.position_id = None

            # Cancel any trailing stops connected to the position
            if self.trailing_stop:
                self.log.info(f"self.trailing_stop")
                self.cancel_order(self.trailing_stop)
                self.trailing_stop = None

    def on_save(self) -> dict[str, bytes]:
        """
        Actions to be performed when the strategy is saved.

        Create and return a state dictionary of values to be saved.

        Returns
        -------
        dict[str, bytes]
            The strategy state dictionary.

        """
        self.log.info("on_save")
        return {}

    def on_load(self, state: dict[str, bytes]):
        """
        Actions to be performed when the strategy is loaded.

        Saved state values will be contained in the give state dictionary.

        Parameters
        ----------
        state : dict[str, bytes]
            The strategy state dictionary.

        """
        self.log.info("on_load")

    def on_dispose(self):
        """
        Actions to be performed when the strategy is disposed.

        Cleanup any resources used by the strategy here.

        """
        self.log.info("on_dispose")

    #### USER METHODS ####
    def entry_buy(self):
        """
        Users simple buy entry method (example).
        """
        if not self.instrument:
            self.log.error("No instrument loaded.")
            return

        order: MarketOrder = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.BUY,
            quantity=self.instrument.make_qty(self.trade_size),
        )

        self.entry = order

        try:
            self.submit_order(order)
        except Exception as e:
            self.log.error(f"Error submitting order {e}")

    def entry_sell(self):
        """
        Users simple sell entry method (example).
        """
        if not self.instrument:
            self.log.error("No instrument loaded.")
            return

        order: MarketOrder = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.SELL,
            quantity=self.instrument.make_qty(self.trade_size),
        )

        self.entry = order

        try:
            self.submit_order(order)
        except Exception as e:
            self.log.error(f"Error submitting order {e}")

    def add_trailing_stop(self, event):
        """
       Users simple trailing stop
       """

        if not self.instrument:
            self.log.error("No instrument loaded.")
            return
        trailing_stop_side = OrderSide.SELL if event.entry == OrderSide.BUY else OrderSide.BUY

        trailing_offset = self.atr.value * self.trailing_atr_multiple

        trailing_offset = np.min([
            np.max([
                10, Decimal(f"{trailing_offset}")
            ]),
            500])
        trailing_offset = round(trailing_offset / 100,
                                1) * 100  # fixme binance limits 0.1-5 % or 10-500 in BASIS_POINTS

        activation_percentage = self.activation_percentage
        assert activation_percentage >= 0 and activation_percentage <= 1, "activation_percentage should be 0 <= & <= 1"
        activationPrice = float(event.avg_px_open) * (
                1 + activation_percentage) if event.entry == OrderSide.BUY else \
            float(event.avg_px_open) * (1 - activation_percentage)

        activationPrice = Decimal(f"{activationPrice:.{self.instrument.price_precision}f}")

        order: TrailingStopMarketOrder = self.order_factory.trailing_stop_market(
            instrument_id=self.instrument_id,
            order_side=trailing_stop_side,
            quantity=self.instrument.make_qty(self.trade_size),
            # trailing_offset=300,
            # trailing_offset=Decimal(f"{trailing_offset:.{self.instrument.price_precision}f}"),
            trailing_offset=trailing_offset,
            trailing_offset_type=self.trailing_offset_type,
            # trigger_price=Price.from_str(f'{event.avg_px_open}'),
            trigger_price=Price.from_str(f'{activationPrice}'),
            trigger_type=self.trigger_type,
            reduce_only=True,
            emulation_trigger=self.emulation_trigger,
        )

        self.trailing_stop = order
        self.submit_order(order, position_id=self.position_id)
