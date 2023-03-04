import numpy as np
import pandas as pd


def sample_arb_strategy(
OHLCV_Data,
        R_parameters,
        **strategy_kwargs):
    """
    """
    # todo check for close to be vbt.Data object or convert to vbt.Data object
    import vectorbtpro as vbt



    # features = data.run("talib_all", periods=vbt.run_func_dict(talib_mavp=14))

    bb = OHLCV_Data.run("bbands")
    entries = OHLCV_Data.hlc3.vbt.crossed_above(bb.upper) & (bb.bandwidth < 0.1)
    exits = OHLCV_Data.hlc3.vbt.crossed_below(bb.upper) & (bb.bandwidth > 0.5)
    short_entries = OHLCV_Data.hlc3.vbt.crossed_below(bb.lower) & (bb.bandwidth < 0.1)
    short_exits = OHLCV_Data.hlc3.vbt.crossed_above(bb.lower) & (bb.bandwidth > 0.5)
    # pf = vbt.PF.from_signals(OHLCV_Data, entries, exits, short_entries, short_exits)
    # pf.plot_trade_signals().show()

    # Get a df of exits/short_exits = 0 while entries = 1 and short_entries = -1 else 0

    side = pd.DataFrame(
        np.where(entries, 1, np.where(exits, 0, np.where(short_entries, -1, np.where(short_exits, 0, 0)))),
        index=OHLCV_Data.index,
        columns=OHLCV_Data.columns
    )

    return side
