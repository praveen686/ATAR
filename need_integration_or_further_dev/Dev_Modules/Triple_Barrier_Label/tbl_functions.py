import os.path

import numpy as np
import pandas as pd

from need_integration_or_further_dev.Standard_Algorythms import util
from need_integration_or_further_dev.Standard_Algorythms.labeling_algorythms import labeling
from need_integration_or_further_dev.Standard_Algorythms.timeseries_algorythms import timeseries_filters
from need_integration_or_further_dev.Dev_Modules.Triple_Barrier_Label.tbl_help import train_model, \
    load_primary_n_meta_model_pickles, \
    save_primary_n_meta_model_pickles, live_execution_of_models


def daily_vol_triple_barrier_label_example(close_series, side_series,
                                           **tbl_kwargs):  # todo add more inputs used in the func
    """
    This function is a sample of how to use the triple barrier labeling algorythm

    Primary Model is used to generate the side series

    """
    # Import packages

    # Check inputs todo
    assert isinstance(close_series, pd.Series)
    assert isinstance(side_series, pd.Series)
    assert close_series.index.equals(side_series.index)

    '''Primary Model'''
    # Combine the side series with the close series
    side_labeled_ohlcv_data = pd.concat([close_series, side_series], axis=1, keys=['close', 'side'])

    # Remove Look ahead biase by lagging the signal
    side_labeled_ohlcv_data['side'] = side_labeled_ohlcv_data['side'].shift(1)  # Needed for the labeling algorythm

    # hotfix
    test_n_elements = tbl_kwargs.get('test_n_elements', None)
    if test_n_elements:
        side_labeled_ohlcv_data = side_labeled_ohlcv_data[:test_n_elements]

    # Save the raw data
    raw_data = side_labeled_ohlcv_data.copy()

    # Drop the NaN values from our data set
    side_labeled_ohlcv_data = side_labeled_ohlcv_data.dropna(axis=0, how='any', inplace=False)

    # Make sure side is an integer
    side_labeled_ohlcv_data['side'] = side_labeled_ohlcv_data['side'].astype(int)

    # Compute daily volatility
    daily_vol = util.get_daily_vol(close=side_labeled_ohlcv_data['close'], lookback=50)

    # Apply Symmetric CUSUM Filter and get timestamps for events
    # Note: Only the CUSUM filter needs a point estimate for volatility
    cusum_events = timeseries_filters.cusum_filter(side_labeled_ohlcv_data['close'], threshold=daily_vol.mean() * 0.5)

    # Compute vertical barrier
    vertical_barriers = labeling.add_vertical_barrier(t_events=cusum_events, close=side_labeled_ohlcv_data['close'],
                                                      # num_days=1, num_hours=0, num_minutes=0, num_seconds=0
                                                      num_days=tbl_kwargs.get('vertical_barrier_num_days', 1),
                                                      num_hours=tbl_kwargs.get('vertical_barrier_num_hours', 0),
                                                      num_minutes=tbl_kwargs.get('vertical_barrier_num_minutes', 0),
                                                      num_seconds=tbl_kwargs.get('vertical_barrier_num_seconds', 0)
                                                      )

    triple_barrier_events = labeling.get_events(close=side_labeled_ohlcv_data['close'],
                                                t_events=cusum_events,
                                                pt_sl=tbl_kwargs.get('pt_sl', [1, 1]),
                                                target=daily_vol,
                                                vertical_barrier_times=vertical_barriers,
                                                min_ret=tbl_kwargs.get('min_ret', 0.001),
                                                num_threads=tbl_kwargs.get('num_threads', 1),
                                                side_prediction=side_labeled_ohlcv_data['side'])

    labels = labeling.get_bins(triple_barrier_events, side_labeled_ohlcv_data['close'])

    # Shift the side series back to the original position
    raw_data.dropna(axis=0, how='any', inplace=True)
    raw_data['side'] = raw_data['side'].astype(int)

    # Change raw_data side name to direction
    raw_data.rename(columns={'side': 'direction'}, inplace=True)

    # labels.columns = ["ret", "trgt_ret", "bin", "label_side"]
    labels.columns = ["ret", "target_ret", "meta_target", "prim_target"]

    returning_df = pd.concat([raw_data, labels], axis=1).fillna(0)

    # Add the first row since they were removed in the beginning after the lagging. Include dates
    first_row = {'close': close_series[0], 'direction': side_series[0], 'ret': 0, 'target_ret': 0, 'meta_target': 0,
                 'prim_target': 0}
    first_row = pd.DataFrame(first_row, index=[close_series.index[0]])
    returning_df = pd.concat([first_row, returning_df], axis=0)

    # Change prim_target and meta_target to int
    returning_df['prim_target'] = returning_df['prim_target'].astype(int)
    returning_df['meta_target'] = returning_df['meta_target'].astype(int)

    print("TBL-ML-Data")
    print(returning_df[["direction", "prim_target", "meta_target"]].head(10))

    # Print unique values
    unique_values = returning_df[["direction", "prim_target", "meta_target"]].apply(lambda x: x.unique())
    print(unique_values)

    return returning_df
