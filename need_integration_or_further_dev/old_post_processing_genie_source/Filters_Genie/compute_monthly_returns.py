import pandas as pd
# noinspection PyUnresolvedReferences
import ray
import vectorbtpro as vbt
# noinspection PyUnresolvedReferences
from logger_tt import logger

from Equipment_Handler.equipment_handler import CHECKTEMPS
from Equipment_Handler.equipment_settings import TEMP_DICT
from Filters_Genie import utils as _utils


@vbt.chunked(
    n_chunks=2,
    # size=vbt.LenSizer(arg_query='only_these_stats'),
    size=vbt.ShapeSizer(arg_query="returns_shape", axis=1),
    # size=Porfolio.wrapper.columns.shape[0],
    arg_take_spec=dict(
        # pf=vbt.ChunkSlicer(),
        returns_chunk=vbt.ChunkSlicer(),
        eoy=None,
        compounded=None,
        prepare_returns=None,
    ),
    merge_func=lambda x: pd.concat(x, axis=0),  #
    show_progress=True,
    engine='ray',
    init_kwargs={
        # 'address': 'auto',
        # 'num_cpus': 28,
        # 'memory': 100 * 10 ** 9,
        # 'object_store_memory': 100 * 10 ** 9,
    },
)
def monthly_returns_ray_chunk(returns, eoy=False, compounded=False, prepare_returns=True):
    """Calculates monthly returns"""
    if isinstance(returns, pd.DataFrame):
        returns = returns.copy()
        returns.columns = map(str.lower, returns.columns)
        if len(returns.columns) > 1 and 'close' in returns.columns:
            returns = returns['close']
        else:
            returns = returns[returns.columns[0]]

    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    original_returns = returns.copy()
    print(returns)

    returns = pd.DataFrame(
        _utils.group_returns(returns,
                             # returns.index.strftime('%Y-%m-01'),
                             returns.vbt.resample_apply("M", vbt.nb.sum_reduce_nb),
                             compounded))

    returns.columns = ['Returns']
    returns.index = pd.to_datetime(returns.index)

    # get returnsframe
    returns['Year'] = returns.index.strftime('%Y')
    returns['Month'] = returns.index.strftime('%b')
    # print(returns)
    # print()

    # make pivot table
    returns = returns.pivot('Year', 'Month', 'Returns').fillna(0)
    # print(returns)
    # print()
    # print()
    # print()

    # handle missing months
    months_present = []
    for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
        if month not in returns.columns:
            returns.loc[:, month] = 0
        else:
            months_present.append(month)

    # order columns by month
    returns = returns[months_present]

    if eoy:
        returns['eoy'] = _utils.group_returns(
            original_returns, original_returns.index.year).values

    # returns.columns = map(lambda x: str(x).upper(), returns.columns)
    # returns.index.name = None

    return returns


@ray.remote
def monthly_returns(returns, eoy=False, compounded=False, prepare_returns=True):
    CHECKTEMPS(TEMP_DICT)
    """Calculates monthly returns"""
    if isinstance(returns, pd.DataFrame):
        returns = returns.copy()
        returns.columns = map(str.lower, returns.columns)
        if len(returns.columns) > 1 and 'close' in returns.columns:
            returns = returns['close']
        else:
            returns = returns[returns.columns[0]]

    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    original_returns = returns.copy()

    returns = pd.DataFrame(
        _utils.group_returns(returns,
                             returns.index.strftime('%Y-%m-01'),
                             # returns.vbt.resample_apply("M", vbt.nb.sum_reduce_nb),
                             compounded))

    returns.columns = ['Returns']
    returns.index = pd.to_datetime(returns.index)

    # get returnsframe
    returns['Year'] = returns.index.strftime('%Y')
    returns['Month'] = returns.index.strftime('%b')

    # make pivot table
    returns = returns.pivot('Year', 'Month', 'Returns').fillna(0)

    # handle missing months
    months_present = []
    for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
        if month in returns.columns:
            months_present.append(month)

    # order columns by month

    returns = returns[months_present]

    if eoy:
        returns['eoy'] = _utils.group_returns(
            original_returns, original_returns.index.year).values

    returns.columns = map(lambda x: str(x).upper(), returns.columns)
    returns.index.name = 'Months'

    return returns


@ray.remote
def monthly_returns_chunks(returns, column, eoy=False, compounded=False, prepare_returns=True):
    return ray.get(
        monthly_returns.remote(returns[column], eoy=eoy, compounded=compounded, prepare_returns=prepare_returns))


import vectorbtpro as vbt


def monthly_returns_multiindex(returns, eoy=False, compounded=False, prepare_returns=True):
    # returns_shape = returns.shape
    #
    # ray_result = monthly_returns_ray_chunk(
    #     returns, returns_shape, eoy=eoy, compounded=compounded,
    #     prepare_returns=prepare_returns)
    # # logger.info(ray_result)
    # exit()
    #
    returns_id = ray.put(returns)
    # logger.info(f'1{returns.columns = }')

    ray_result = ray.get([
        monthly_returns_chunks.remote(
            returns_id, col_name, eoy=eoy, compounded=compounded,
            prepare_returns=prepare_returns) for col_name in returns.columns
    ])
    #
    results = pd.concat(ray_result, axis=0)
    results = results.set_index(returns.columns)
    return results
    #
