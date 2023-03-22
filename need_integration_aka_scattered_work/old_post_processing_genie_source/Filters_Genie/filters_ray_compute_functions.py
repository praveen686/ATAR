import pandas as pd
import ray


@ray.remote
def concat_columns_remote(function, ncols):
    return pd.concat([function(column=i) for i in range(ncols)], axis=1)


@ray.remote
def returns_qs_accessor_remote(returns, freq='d', to_vbt_returns=True):
    # noinspection PyUnresolvedReferences
    import vectorbtpro as vbt
    print(f"Preparing QS accessor for freq = {freq}")

    result = returns.vbt.resample_apply(freq, vbt.nb.sum_reduce_nb)
    if to_vbt_returns:
        result = result.vbt.returns(freq=freq)
    #
    return result
