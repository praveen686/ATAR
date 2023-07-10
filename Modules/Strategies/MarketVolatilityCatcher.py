import math
from datetime import timedelta
from decimal import Decimal
from decimal import ROUND_DOWN
from typing import Optional
from typing import Union

from nautilus_trader.common.enums import LogColor
from nautilus_trader.common.timer import TimeEvent
from nautilus_trader.config import StrategyConfig
from nautilus_trader.config.common import ExecAlgorithmConfig
from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.core.data import Data
from nautilus_trader.core.message import Event
from nautilus_trader.execution.algorithm import ExecAlgorithm
from nautilus_trader.indicators.atr import AverageTrueRange
from nautilus_trader.model.data.bar import Bar
from nautilus_trader.model.data.bar import BarType
from nautilus_trader.model.data.book import OrderBookDelta
from nautilus_trader.model.data.tick import QuoteTick
from nautilus_trader.model.data.tick import TradeTick
from nautilus_trader.model.data.ticker import Ticker
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import OrderType
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.enums import TriggerType
from nautilus_trader.model.events.order import OrderFilled
from nautilus_trader.model.identifiers import ClientOrderId
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.objects import Quantity
from nautilus_trader.model.orderbook import OrderBook
from nautilus_trader.model.orders import LimitOrder
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.model.orders import Order
from nautilus_trader.trading.strategy import Strategy


class MarketVolatilityCatcherConfig(StrategyConfig, frozen=True):
    """
    Configuration for ``VolatilityMarketMaker`` instances.

    Parameters
    ----------
    instrument_id : InstrumentId
        The instrument ID for the strategy.
    bar_type : BarType
        The bar type for the strategy.
    atr_period : int
        The period for the ATR indicator.
    atr_multiple : float
        The ATR multiple for bracketing limit orders.
    trade_size : Decimal
        The position size per trade.
    order_id_tag : str
        The unique order ID tag for the strategy. Must be unique
        amongst all running strategies for a particular trader ID.
    emulation_trigger : str, default 'NO_TRIGGER'
        The emulation trigger for submitting emulated orders.
        If ``None`` then orders will not be emulated.
    oms_type : OmsType
        The order management system type for the strategy. This will determine
        how the `ExecutionEngine` handles position IDs (see docs).
    """

    instrument_id: str
    bar_type: str
    atr_period: int
    atr_multiple: float
    trade_size: Decimal
    emulation_trigger: str = "NO_TRIGGER"


class MarketVolatilityCatcher(Strategy):
    """
    A very dumb market maker which brackets the current market based on
    volatility measured by an ATR indicator.

    Cancels all orders and closes all positions on stop.

    Parameters
    ----------
    config : VolatilityMarketMakerConfig
        The configuration for the instance.
    """

    def __init__(self, config: MarketVolatilityCatcherConfig) -> None:
        super().__init__(config)

        # Configuration
        self.instrument_id = InstrumentId.from_str(config.instrument_id)
        self.bar_type = BarType.from_str(config.bar_type)
        self.atr_multiple = config.atr_multiple
        self.trade_size = Decimal(config.trade_size)
        self.emulation_trigger = TriggerType[config.emulation_trigger]

        # Create the indicators for the strategy
        self.atr = AverageTrueRange(config.atr_period)

        self.instrument: Optional[Instrument] = None  # Initialized in on_start

        # Users order management variables
        self.buy_order: Union[LimitOrder, None] = None
        self.sell_order: Union[LimitOrder, None] = None

    def on_start(self) -> None:
        """Actions to be performed on strategy start."""
        self.instrument = self.cache.instrument(self.instrument_id)
        if self.instrument is None:
            self.log.error(f"Could not find instrument for {self.instrument_id}")
            self.stop()
            return

        # Register the indicators for updating
        self.register_indicator_for_bars(self.bar_type, self.atr)

        # Get historical data
        self.request_bars(self.bar_type)

        # Subscribe to live data
        self.subscribe_bars(self.bar_type)
        self.subscribe_quote_ticks(self.instrument_id)
        # self.subscribe_trade_ticks(self.instrument_id)
        # self.subscribe_ticker(self.instrument_id)  # For debugging
        # self.subscribe_order_book_deltas(self.instrument_id, depth=50)  # For debugging
        # self.subscribe_order_book_snapshots(
        #     self.instrument_id,
        #     depth=20,
        #     interval_ms=1000,
        # )  # For debugging
        # self.subscribe_data(
        #     data_type=DataType(
        #         BinanceFuturesMarkPriceUpdate, metadata={"instrument_id": self.instrument.id}
        #     ),
        #     client_id=ClientId("BINANCE"),
        # )

    def on_data(self, data: Data) -> None:
        """
        Actions to be performed when the strategy is running and receives generic
        data.

        Parameters
        ----------
        data : Data
            The data received.

        """
        # For debugging (must add a subscription)
        # self.log.info(repr(data), LogColor.CYAN)

    def on_instrument(self, instrument: Instrument) -> None:
        """
        Actions to be performed when the strategy is running and receives an
        instrument.

        Parameters
        ----------
        instrument : Instrument
            The instrument received.

        """
        # For debugging (must add a subscription)
        self.log.info(repr(instrument), LogColor.CYAN)

    def on_order_book(self, order_book: OrderBook) -> None:
        """
        Actions to be performed when the strategy is running and receives an order book.

        Parameters
        ----------
        order_book : OrderBook
            The order book received.

        """
        # For debugging (must add a subscription)
        self.log.info(repr(order_book), LogColor.CYAN)

    def on_order_book_delta(self, delta: OrderBookDelta) -> None:
        """
        Actions to be performed when the strategy is running and receives an order book delta.

        Parameters
        ----------
        delta : OrderBookDelta
            The order book delta received.

        """
        # For debugging (must add a subscription)
        self.log.info(repr(delta), LogColor.CYAN)

    def on_ticker(self, ticker: Ticker) -> None:
        """
        Actions to be performed when the strategy is running and receives a ticker.

        Parameters
        ----------
        ticker : Ticker
            The ticker received.

        """
        # For debugging (must add a subscription)
        self.log.info(repr(ticker), LogColor.CYAN)

    def on_quote_tick(self, tick: QuoteTick) -> None:
        """
        Actions to be performed when the strategy is running and receives a quote tick.

        Parameters
        ----------
        tick : QuoteTick
            The tick received.

        """
        # For debugging (must add a subscription)
        self.log.info(repr(tick), LogColor.CYAN)

    def on_trade_tick(self, tick: TradeTick) -> None:
        """
        Actions to be performed when the strategy is running and receives a trade tick.

        Parameters
        ----------
        tick : TradeTick
            The tick received.

        """
        # For debugging (must add a subscription)
        self.log.info(repr(tick), LogColor.CYAN)

    def on_bar(self, bar: Bar) -> None:
        """
        Actions to be performed when the strategy is running and receives a bar.

        Parameters
        ----------
        bar : Bar
            The bar received.

        """

        self.log.info(repr(bar), LogColor.CYAN)
        #
        # Check if indicators ready
        if not self.indicators_initialized():
            self.log.info(
                f"Waiting for indicators to warm up " f"[{self.cache.bar_count(self.bar_type)}]...",
                color=LogColor.BLUE,
            )
            return  # Wait for indicators to warm up...

        last: QuoteTick = self.cache.quote_tick(self.instrument_id)
        self.log.info(repr(last), LogColor.CYAN)
        if last is None:
            self.log.info("No quotes yet...")
            return

        # Maintain buy orders
        if self.buy_order and (self.buy_order.is_emulated or self.buy_order.is_open):
            self.cancel_order(self.buy_order)
        self.create_buy_order(last)

        # Maintain sell orders
        if self.sell_order and (self.sell_order.is_emulated or self.sell_order.is_open):
            self.cancel_order(self.sell_order)
        self.create_sell_order(last)

    def create_buy_order(self, last: QuoteTick) -> None:
        """
        Market maker simple buy limit method (example).
        """
        if not self.instrument:
            self.log.error("No instrument loaded.")
            return

        price: Decimal = last.bid - (self.atr.value * self.atr_multiple)
        order: LimitOrder = self.order_factory.limit(
            instrument_id=self.instrument_id,
            order_side=OrderSide.BUY,
            quantity=self.instrument.make_qty(self.trade_size),
            price=self.instrument.make_price(price),
            time_in_force=TimeInForce.GTC,
            post_only=True,  # default value is True
            # display_qty=self.instrument.make_qty(self.trade_size / 2),  # iceberg
            emulation_trigger=self.emulation_trigger,
        )

        self.buy_order = order
        self.submit_order(order)

    def create_sell_order(self, last: QuoteTick) -> None:
        """
        Market maker simple sell limit method (example).
        """
        if not self.instrument:
            self.log.error("No instrument loaded.")
            return

        price: Decimal = last.ask + (self.atr.value * self.atr_multiple)
        order: LimitOrder = self.order_factory.limit(
            instrument_id=self.instrument_id,
            order_side=OrderSide.SELL,
            quantity=self.instrument.make_qty(self.trade_size),
            price=self.instrument.make_price(price),
            time_in_force=TimeInForce.GTC,
            post_only=True,  # default value is True
            # display_qty=self.instrument.make_qty(self.trade_size / 2),  # iceberg
            emulation_trigger=self.emulation_trigger,
        )

        self.sell_order = order
        self.submit_order(order)

    def on_event(self, event: Event) -> None:
        """
        Actions to be performed when the strategy is running and receives an event.

        Parameters
        ----------
        event : Event
            The event received.

        """
        last: QuoteTick = self.cache.quote_tick(self.instrument_id)
        if last is None:
            self.log.info("No quotes yet...")
            return

        # If order filled then replace order at atr multiple distance from the market
        if isinstance(event, OrderFilled):
            if self.buy_order and event.order_side == OrderSide.BUY:
                if self.buy_order.is_closed:
                    self.create_buy_order(last)
            elif (
                    self.sell_order and event.order_side == OrderSide.SELL and self.sell_order.is_closed
            ):
                self.create_sell_order(last)

    def on_stop(self) -> None:
        """
        Actions to be performed when the strategy is stopped.
        """
        self.cancel_all_orders(self.instrument_id)
        self.close_all_positions(self.instrument_id)

        # Unsubscribe from data
        self.unsubscribe_bars(self.bar_type)
        self.unsubscribe_quote_ticks(self.instrument_id)

    def on_reset(self) -> None:
        """
        Actions to be performed when the strategy is reset.
        """
        # Reset indicators here
        self.atr.reset()

    def on_save(self) -> dict[str, bytes]:
        """
        Actions to be performed when the strategy is saved.

        Create and return a state dictionary of values to be saved.

        Returns
        -------
        dict[str, bytes]
            The strategy state dictionary.

        """
        return {}

    def on_load(self, state: dict[str, bytes]) -> None:
        """
        Actions to be performed when the strategy is loaded.

        Saved state values will be contained in the give state dictionary.

        Parameters
        ----------
        state : dict[str, bytes]
            The strategy state dictionary.

        """

    def on_dispose(self) -> None:
        """
        Actions to be performed when the strategy is disposed.

        Cleanup any resources used by the strategy here.

        """


class TWAPExecAlgorithmConfig(ExecAlgorithmConfig, frozen=True):
    """
    Configuration for ``TWAPExecAlgorithm`` instances.

    This configuration class defines the necessary parameters for a Time-Weighted Average Price
    (TWAP) execution algorithm, which aims to execute orders evenly spread over a specified
    time horizon, at regular intervals.

    Parameters
    ----------
    exec_algorithm_id : InstrumentId
        The execution algorithm ID (will override default which is the class name).
    """

    exec_algorithm_id: Optional[str] = "TWAP"


class TWAPExecAlgorithm(ExecAlgorithm):
    """
    Provides a Time-Weighted Average Price (TWAP) execution algorithm.

    The TWAP execution algorithm aims to execute orders by evenly spreading them over a specified
    time horizon. The algorithm receives a primary order representing the total size and direction
    then splits this by spawning smaller child orders, which are then executed at regular intervals
    throughout the time horizon.

    This helps to reduce the impact of the full size of the primary order on the market, by
    minimizing the concentration of trade size at any given time.

    The algorithm will immediately submit the first order, with the final order submitted being the
    primary order at the end of the horizon period.

    Parameters
    ----------
    config : TWAPExecAlgorithmConfig, optional
        The configuration for the instance.
    """

    def __init__(self, config: Optional[TWAPExecAlgorithmConfig] = None) -> None:
        if config is None:
            config = TWAPExecAlgorithmConfig()
        super().__init__(config)

        self._scheduled_sizes: dict[ClientOrderId, list[Quantity]] = {}

    def on_start(self) -> None:
        """Actions to be performed when the algorithm component is started."""
        # Optionally implement

    def on_stop(self) -> None:
        """Actions to be performed when the algorithm component is stopped."""
        self.clock.cancel_timers()

    def on_reset(self) -> None:
        """Actions to be performed when the algorithm component is reset."""
        self._scheduled_sizes.clear()

    def on_save(self) -> dict[str, bytes]:
        """
        Actions to be performed when the algorithm component is saved.

        Create and return a state dictionary of values to be saved.

        Returns
        -------
        dict[str, bytes]
            The strategy state dictionary.

        """
        return {}  # Optionally implement

    def on_load(self, state: dict[str, bytes]) -> None:
        """
        Actions to be performed when the algorithm component is loaded.

        Saved state values will be contained in the give state dictionary.

        Parameters
        ----------
        state : dict[str, bytes]
            The algorithm component state dictionary.

        """
        # Optionally implement

    def round_decimal_down(self, amount: Decimal, precision: int) -> Decimal:
        return amount.quantize(Decimal(f"1e-{precision}"), rounding=ROUND_DOWN)

    def on_order(self, order: Order) -> None:  # noqa (too complex)
        """
        Actions to be performed when running and receives an order.

        Parameters
        ----------
        order : Order
            The order to be handled.

        Warnings
        --------
        System method (not intended to be called by user code).

        """
        PyCondition.not_in(
            order.client_order_id,
            self._scheduled_sizes,
            "order.client_order_id",
            "self._scheduled_sizes",
        )
        self.log.info(repr(order), LogColor.CYAN)

        if order.order_type != OrderType.MARKET:
            self.log.error(
                f"Cannot execute order: only implemented for market orders, {order.order_type=}.",
            )
            return

        instrument = self.cache.instrument(order.instrument_id)
        if not instrument:
            self.log.error(
                f"Cannot execute order: instrument {order.instrument_id} not found.",
            )
            return

        # Validate execution parameters
        exec_params = order.exec_algorithm_params
        if not exec_params:
            self.log.error(
                f"Cannot execute order: "
                f"`exec_algorithm_params` not found for primary order {order!r}.",
            )
            return

        horizon_secs = exec_params.get("horizon_secs")
        if not horizon_secs:
            self.log.error(
                f"Cannot execute order: "
                f"`horizon_secs` not found in `exec_algorithm_params` {exec_params}.",
            )
            return

        interval_secs = exec_params.get("interval_secs")
        if not interval_secs:
            self.log.error(
                f"Cannot execute order: "
                f"`interval_secs` not found in `exec_algorithm_params` {exec_params}.",
            )
            return

        if horizon_secs < interval_secs:
            self.log.error(
                f"Cannot execute order: " f"{horizon_secs=} was less than {interval_secs=}.",
            )
            return

        # Calculate the number of intervals
        num_intervals: int = math.floor(horizon_secs / interval_secs)

        # Divide the order quantity evenly and determine any remainder
        quotient = order.quantity.as_decimal() / num_intervals
        floored_quotient = self.round_decimal_down(quotient, instrument.size_precision)
        qty_quotient = instrument.make_qty(floored_quotient)
        qty_per_interval = instrument.make_qty(qty_quotient)
        qty_remainder = order.quantity.as_decimal() - (floored_quotient * num_intervals)

        if qty_per_interval < instrument.size_increment:
            self.log.error(
                f"Cannot execute order: "
                f"{qty_per_interval=} less than {instrument.id} {instrument.size_increment}.",
            )
            return

        if instrument.min_quantity and qty_per_interval < instrument.min_quantity:
            self.log.error(
                f"Cannot execute order: "
                f"{qty_per_interval=} less than {instrument.id} {instrument.min_quantity=}.",
            )
            return

        scheduled_sizes: list[Quantity] = [qty_per_interval] * num_intervals

        if qty_remainder:
            scheduled_sizes.append(instrument.make_qty(qty_remainder))

        assert sum(scheduled_sizes) == order.quantity
        self.log.info(f"Order execution size schedule: {scheduled_sizes}.", LogColor.BLUE)

        # Immediately submit first order
        if qty_per_interval == order.quantity:
            self.log.warning(f"Submitting for entire size {qty_per_interval=}, {order.quantity=}.")
            self.submit_order(order)
            return  # Done

        self._scheduled_sizes[order.client_order_id] = scheduled_sizes
        first_qty: Quantity = scheduled_sizes.pop(0)

        spawned_order: MarketOrder = self.spawn_market(
            primary=order,
            quantity=first_qty,
            time_in_force=order.time_in_force,
            reduce_only=order.is_reduce_only,
            tags=order.tags,
        )

        self.submit_order(spawned_order)

        # Setup timer
        self.clock.set_timer(
            name=order.client_order_id.value,
            interval=timedelta(seconds=interval_secs),
            callback=self.on_time_event,
        )
        self.log.info(
            f"Started TWAP execution for {order.client_order_id}: "
            f"{horizon_secs=}, {interval_secs=}.",
            LogColor.BLUE,
        )

    def on_time_event(self, event: TimeEvent) -> None:
        """
        Actions to be performed when the algorithm receives a time event.

        Parameters
        ----------
        event : TimeEvent
            The time event received.

        """
        self.log.info(repr(event), LogColor.CYAN)

        exec_spawn_id = ClientOrderId(event.name)

        primary: Order = self.cache.order(exec_spawn_id)
        if not primary:
            self.log.error(f"Cannot find primary order for {exec_spawn_id=}")
            return

        if primary.is_closed:
            self.complete_sequence(primary.client_order_id)
            return

        instrument: Instrument = self.cache.instrument(primary.instrument_id)
        if not instrument:
            self.log.error(
                f"Cannot execute order: instrument {primary.instrument_id} not found.",
            )
            return

        scheduled_sizes = self._scheduled_sizes.get(exec_spawn_id)
        if scheduled_sizes is None:
            self.log.error(f"Cannot find scheduled sizes for {exec_spawn_id=}")
            return

        if not scheduled_sizes:
            self.log.warning(f"No more size to execute for {exec_spawn_id=}")
            return

        quantity: Quantity = instrument.make_qty(scheduled_sizes.pop(0))
        if not scheduled_sizes:  # Final quantity
            self.submit_order(primary)
            self.complete_sequence(primary.client_order_id)
            return

        spawned_order: MarketOrder = self.spawn_market(
            primary=primary,
            quantity=quantity,
            time_in_force=primary.time_in_force,
            reduce_only=primary.is_reduce_only,
            tags=primary.tags,
        )

        self.submit_order(spawned_order)

    def complete_sequence(self, exec_spawn_id: ClientOrderId) -> None:
        """
        Complete an execution sequence.

        Parameters
        ----------
        exec_spawn_id : ClientOrderId
            The execution spawn ID to complete.

        """
        if exec_spawn_id.value in self.clock.timer_names:
            self.clock.cancel_timer(exec_spawn_id.value)
        self._scheduled_sizes.pop(exec_spawn_id, None)
        self.log.info(f"Completed TWAP execution for {exec_spawn_id}.", LogColor.BLUE)
