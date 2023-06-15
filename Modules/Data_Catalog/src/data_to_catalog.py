from datetime import datetime

import pandas as pd
from nautilus_trader.core.datetime import dt_to_unix_nanos
from nautilus_trader.model.data.tick import QuoteTick
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.objects import Price, Quantity


def custom_parser_text_line(line, instrument_id: InstrumentId, datatime_format="%Y%m%d %H%M%S%f", header=None):
    ts, bid, ask, idx = line.split(b",")
    dt = pd.Timestamp(
        datetime.strptime(ts.decode(), datatime_format),
        tz="UTC",
    )
    ts = dt_to_unix_nanos(dt)
    yield QuoteTick(
        instrument_id=instrument_id,
        bid=Price.from_str(bid.decode()),
        ask=Price.from_str(ask.decode()),
        bid_size=Quantity.from_int(100_000),
        ask_size=Quantity.from_int(100_000),
        ts_event=ts,
        ts_init=ts,
    )


def custom_parser_csv(data, instrument_id, datetime_format="%Y.%m.%d %H:%M:%S.%f"): # fixme not flexible for headers
    """ Parser function for hist_data FX data, for use with CSV Reader """

    dt = pd.Timestamp(datetime.strptime(data['DateTime'].decode(), datetime_format), tz='UTC')
    ts = dt_to_unix_nanos(dt)

    # Header Specific below v
    bid = data["Bid"].decode()
    ask = data["Ask"].decode()
    total_volume = data["Total volume\r"].decode()
    # Header Specific above ^


    bid = Price.from_str(bid)
    ask = Price.from_str(ask)
    total_volume = Quantity.from_str(total_volume)
    if bid.precision != ask.precision:
        # Get the highest precision
        precision = max(bid.precision, ask.precision)
        bid = f"{bid.as_double():.{precision}f}"
        ask = f"{ask.as_double():.{precision}f}"
        #
        bid = Price.from_str(bid)
        ask = Price.from_str(ask)

    yield QuoteTick(
        instrument_id=instrument_id,
        bid=bid,
        ask=ask,
        bid_size=total_volume,
        ask_size=total_volume,
        ts_event=ts,
        ts_init=ts,
    )