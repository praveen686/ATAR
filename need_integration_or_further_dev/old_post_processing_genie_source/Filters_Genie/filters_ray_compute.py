import ray


@ray.remote
def genie_compute_drawdowns_remote(ret_accs):
    from Filters_Genie.filters_ray_compute_functions import concat_columns_remote
    #
    drawdowns = ray.get(
        [
            concat_columns_remote.remote(ret_.qs.to_drawdown_series, len(ret_.wrapper.columns)) for name, ret_ in
            ret_accs.items()
        ]
    )
    total_drawdown = drawdowns[-1].sum()
    return total_drawdown, *drawdowns


