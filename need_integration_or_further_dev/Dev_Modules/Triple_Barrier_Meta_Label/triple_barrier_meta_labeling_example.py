"""Triple-Barrier and Meta-Labeling: Simplified Explanation

The fixed-time horizon method is a widely-used labeling technique in financial academia. However, it has several
shortcomings, which are addressed by the triple-barrier method. The triple-barrier method can also be combined with
meta-labeling to further enhance its effectiveness.

Sources:

Advances in Financial Machine Learning, Chapter 3 by Marcos Lopez de Prado
Machine Learning for Asset Managers, Chapter 5 by Marcos Lopez de Prado

Triple-Barrier Method:

The triple-barrier method involves three barriers: an upper, a lower, and a vertical barrier. The upper barrier
represents the return threshold for buying opportunities (label 1), the lower barrier represents the return threshold
for selling opportunities (label -1), and the vertical barrier represents the time limit for an observation to reach
either the upper or lower barrier before being labeled 0. This method dynamically adjusts the upper and lower barriers
based on the volatility of each observation.

Meta-Labeling:

Meta-labeling is a secondary machine learning (ML) model that helps determine the appropriate bet size without deciding
the side (long or short) of the bet. The secondary ML model filters false positives from the primary model, increasing
overall accuracy. It has several advantages, including transforming fundamental models into ML models, limiting
overfitting effects, enabling sophisticated strategy structures, and improving decision-making for bet sizing.

How to Use Meta-Labeling:

Build a primary model with high recall, even if the precision is low.
Correct for low precision by applying meta-labeling to the positive predictions of the primary model.
Meta-labeling will improve the F1-score by filtering out false positives, while the primary model identifies most
positives.
Implementation:

Several functions are used for the triple-barrier method in conjunction with meta-labeling. These functions include
add_vertical_barrier(), get_events(), get_bins(), and drop_labels(). Detailed descriptions of these functions can be
found in the original text.

In summary, the triple-barrier method and meta-labeling provide a robust approach to labeling financial data by
addressing the shortcomings of the fixed-time horizon method. The combination of these techniques results in more
accurate predictions and improved decision-making in financial markets."""

import numpy as np
import pandas as pd

from need_integration_or_further_dev.Dev_Modules.genie_loader import Genie_Loader
from need_integration_or_further_dev.Standard_Algorythms import util
from need_integration_or_further_dev.Standard_Algorythms.labeling_algorythms import labeling
from need_integration_or_further_dev.Standard_Algorythms.timeseries_algorythms import timeseries_filters


def sample_arb_strategy(OHLCV_Data):
    """This function takes in OHLCV (Open-High-Low-Close-Volume) data as input and uses it to generate signals for
    entering and exiting trades based on the Bollinger Bands indicator. The function returns a labeled series
    indicating whether the signal is a buy (1), sell (-1), or hold (0) signal."""
    # todo check for close to be vbt.Data object or convert to vbt.Data object
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
    import vectorbtpro as vbt
    features = OHLCV_Data.run("talib_all", periods=vbt.run_func_dict(talib_mavp=14),
                              )

    return side, features


def daily_vol_triple_barrier_label_example(close_series, side_series,
                                           **tbl_kwargs):  # todo add more inputs used in the func
    """
    This function is a sample of how to use the triple barrier labeling algorythm

    This function takes in a series of closing prices and a labeled series generated by the sample_arb_strategy
    function as input. It applies a triple barrier labeling algorithm to the input data to generate a
    meta-labeled series, which is a series of labeled events (0, 1, or -1 & 0 or 1) indicating the success or failure
    of a trade for the primary and for the secondary model. The function returns a DataFrame containing the input data and the meta-labeled series.

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


def save_output_data(output_data, output_file_dir, output_file_name, output_file_type):
    if isinstance(output_file_type, list):
        # This will be a self recursive function
        # assert all the elements in the list are strings
        assert all([isinstance(file_type, str) for file_type in output_file_type])
        for file_type in output_file_type:
            save_output_data(output_data, output_file_dir, output_file_name, file_type)
        return

    if "csv" in output_file_type:
        output_data.to_csv(f"{output_file_dir}/{output_file_name}.csv")
    if "pickle" in output_file_type:
        output_data.to_pickle(f"{output_file_dir}/{output_file_name}.pickle")
    if "vbt" in output_file_type:
        # output_data.to_vbt_pickle(f"{output_file_dir}/{output_file_name}.vbt")
        NotImplementedError("vbt types is not supported yet")


def TBM_labeling(
        input_data_params: dict,
        tbl_params: dict,
        output_data_params: dict,
        **kwargs
):
    """The main script sets up input and output parameters and uses the Genie_Loader module to load the input data from
    a CSV file. It then applies the sample_arb_strategy function to the input data to generate a labeled series.
    The labeled series and the closing price series are then passed to the daily_vol_triple_barrier_label_example
    function to generate a meta-labeled DataFrame. Finally, the script saves the meta-labeled DataFrame to an output
    file using the save_output_data function."""

    """TRIPLE BARRIER Meta LABELING"""
    # Load data and convert to a VBT compatible format for vectorized backtesting e.g. during the side labeling
    genie_loader = Genie_Loader()
    if input_data_params["reload_data"]:
        symbols_data_obj = genie_loader.fetch_data(**input_data_params)
        symbols_data_obj.save(input_data_params["pickle_file_path"])
    else:
        symbols_data_obj = genie_loader.load_vbt_pickle(input_data_params["pickle_file_path"])

    '''Label the sides of the entries when the decision is made, not when the trade is opened -1 0 1 labeled series'''
    # takes no parameter combinations since arbitrary strategy is only needed to handle one asset and one parameter combination
    side_df, features = sample_arb_strategy(
        OHLCV_Data=symbols_data_obj)  # todo just added features, need to finish implementation

    # If mostly empty (features are not used) then drop the features column
    # Description describe() per column
    description = features.describe()
    print(description)

    # Remove columns where mean is in [0, nan, inf, -inf] or count is 0
    columns_to_remove = []
    for column in description.columns:
        if description[column]["mean"] in [0, np.nan, np.inf, -np.inf] or description[column]["count"] == 0 or \
                description[column]["25%"] == description[column]["75%"]:
            columns_to_remove.append(column)
    features = features.drop(columns=columns_to_remove)
    print(f"Removed columns: {columns_to_remove}")
    print(features.head(10))

    '''todo: This is a hotfix due to only working with one asset at the moment'''
    close_series = symbols_data_obj.close  # needs to be only one asset otherwise dimensionality error in multiindex
    side_series = side_df[side_df.keys()[0]]

    '''Using the close and side series and other tbl configuration parameters, label --> triple barrier labeling'''
    triple_barrier_labeled_data = daily_vol_triple_barrier_label_example(close_series=close_series,
                                                                         side_series=side_series, **tbl_params)

    '''Combine the OHLCV data triple barrier labeled data'''
    # remember the close values are the same as the close values in the symbols_data_obj, so we can drop one
    input_ohlcv_df = symbols_data_obj.get()
    triple_barrier_labeled_data = triple_barrier_labeled_data.drop(columns=["close"]).join(input_ohlcv_df).join(
        features)
    triple_barrier_labeled_data.index.names = ["Datetime"]

    # reorder the columns
    triple_barrier_labeled_data = triple_barrier_labeled_data[
        input_ohlcv_df.columns.tolist() + features.columns.tolist() + ["prim_target", "meta_target"]
        ]
    print("triple_barrier_labeled_data")
    # print all columns
    pd.set_option('display.max_columns', None)
    print(triple_barrier_labeled_data)

    '''Save the triple barrier labeled data to be used in other processes'''
    save_output_data(output_data=triple_barrier_labeled_data, **output_data_params)

    return triple_barrier_labeled_data


if __name__ == "__main__":
    # todo:
    #   The biggest assumption this example makes is that your are only owkring with one asset and one parameter
    #       combination unlike how typically Genie is used
    #   This example also assumes working with OHLCV data, that data when passing to strategy function to label sides is
    #       prepared as a vbt.Data object, and that you want to save the output with all the columns plus the labels.
    # Change to working with dask or vectorbt dataframes
    DATA_DIR = "../../../Data"

    INPUT_DATA_PARAMS = dict(
        # todo this will be changed as needed for the endpoint to save the data e.g. S3-bucket
        data_file_dirs=[DATA_DIR],
        data_file_names=["XAUUSD.csv"],
        rename_columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Tick volume": "volume"},
        scheduler='threads',
        first_or_last='first',
        n_rows=None,
        #
        pickle_file_path=f"{DATA_DIR}/XAUUSD.pickle",
        reload_data=True,
    )
    TBL_PARAMS = dict(
        pt_sl=[1, 1],
        min_ret=0.001,
        num_threads=28,
        #
        #  Number of D/H/m/s to add for vertical barrier
        vertical_barrier_num_days=0,
        vertical_barrier_num_hours=4,
        vertical_barrier_num_minutes=0,
        vertical_barrier_num_seconds=0,
    )
    OUTPUT_DATA_PARAMS = dict(
        # todo this will be changed as needed for the endpoint to save the data e.g. S3-bucket
        output_file_dir=DATA_DIR,
        output_file_name="sample_triple_barrier_labeled_data",
        output_file_type=[
            "csv",
            # "pickle"
        ],  # can be csv, pickle, vbt, or list of these
    )

    TBM_labeling(
        input_data_params=INPUT_DATA_PARAMS,
        tbl_params=TBL_PARAMS,
        output_data_params=OUTPUT_DATA_PARAMS,
    )
