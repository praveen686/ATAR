"""
An Overview: Triple-Barrier & Meta-Labeling Techniques

The fixed-time horizon technique, a common strategy for labeling data in the world of financial research, isn't without
its flaws. Enter the triple-barrier method—a more dynamic approach that, when paired with meta-labeling, can
significantly boost efficacy.

From the Writings of Marcos Lopez de Prado:

Advances in Financial Machine Learning, Chapter 3
Machine Learning for Asset Managers, Chapter 5
Breaking Down the Triple-Barrier Method:

Three barriers define this method: the upper, the lower, and the vertical. The upper barrier sets the stage for buying
chances (label 1), while the lower barrier defines selling opportunities (label -1). Finally, the vertical barrier
imposes a time limit on observations, with the upper or lower barriers needing to be reached before an observation is labeled 0. Importantly, this method adjusts the upper and lower barriers based on each observation's volatility.

The Essence of Meta-Labeling:

This secondary machine learning model focuses on determining the optimal bet size, without worrying about the side of
the bet (long or short). As the secondary model filters false positives from the primary model, it bolsters overall
accuracy. Key benefits include morphing fundamental models into machine learning models, curbing overfitting,
developing sophisticated strategy structures, and refining decision-making regarding bet sizes.

Putting Meta-Labeling into Practice:

Develop a primary model with high recall, even if precision is low.
Compensate for low precision by applying meta-labeling to the primary model's positive predictions.
By filtering out false positives, meta-labeling enhances the F1-score while the primary model zeroes in on most
positives.
Implementation in Action:

A variety of functions are employed when using the triple-barrier method in tandem with meta-labeling, such as
add_vertical_barrier(), get_events(), get_bins(), and drop_labels(). Comprehensive descriptions of these functions are
available in the original texts.

In a nutshell, the triple-barrier method and meta-labeling work in concert to create a powerful approach to labeling
financial data, remedying the limitations of the fixed-time horizon method. This harmonious collaboration leads to more
precise predictions and more informed decision-making in the realm of financial markets.
"""
import glob
# Logging
import logging
import os

import numpy as np
import pandas as pd
import vectorbtpro as vbt

from Modules.research_tools.GenieLoader import GenieLoader, fetch_vbt_data
from Modules.research_tools.labeling_algorythms import labeling
from Modules.research_tools.labeling_algorythms.filters import cusum_filter
from Modules.research_tools.labeling_algorythms.trend_scanning import trend_scanning_labels

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


print(f'{vbt.__version__ = }')
logger.info(f'logger{vbt.__version__ = }')

def dataframe_to_series_list(input_dataframe: pd.DataFrame):
    return [s for _, s in input_dataframe.items()]


def example_arb_strategy(VBT_OHLCV_Data):
    """This function takes in OHLCV (Open-High-Low-Close-Volume) data as input and uses it to generate signals for
    entering and exiting trades based on the Bollinger Bands indicator. The function returns a labeled series
    indicating whether the signal is a buy (1), sell (-1), or hold (0) signal."""
    # todo check for close to be vbt.Data object or convert to vbt.Data object
    # features = data.run("talib_all", periods=vbt.run_func_dict(talib_mavp=14))
    bb = VBT_OHLCV_Data.run("bbands")
    entries = VBT_OHLCV_Data.hlc3.vbt.crossed_above(bb.upper) & (bb.bandwidth < 0.1)
    exits = VBT_OHLCV_Data.hlc3.vbt.crossed_below(bb.upper) & (bb.bandwidth > 0.5)
    short_entries = VBT_OHLCV_Data.hlc3.vbt.crossed_below(bb.lower) & (bb.bandwidth < 0.1)
    short_exits = VBT_OHLCV_Data.hlc3.vbt.crossed_above(bb.lower) & (bb.bandwidth > 0.5)
    # pf = vbt.PF.from_signals(OHLCV_Data, entries, exits, short_entries, short_exits) # todo we should do checks after training or at least with the cleaned labeled data
    # pf.plot_trade_signals().show()

    # Get a df of exits/short_exits = 0 while entries = 1 and short_entries = -1 else 0
    side = pd.DataFrame(
        np.where(entries, 1, np.where(exits, 0, np.where(short_entries, -1, np.where(short_exits, 0, 0)))),
        index=VBT_OHLCV_Data.index,
        columns=VBT_OHLCV_Data.columns
    )
    return side


# todo daily_vol_triple_barrier_label_example, generalize , allow to pass in OHLCV data and the name of the volatility function to be used
def volatility_triple_barrier_label_example(
        open_series: pd.Series,
        high_series: pd.Series,
        low_series: pd.Series,
        close_series: pd.Series,
        volume_series: pd.Series,
        side_series: pd.Series, **tbl_kwargs):
    """
    This function is an example of how to use the triple barrier labeling algorythm

    This function takes in a series of closing prices and a labeled series generated by the example_arb_strategy
    function as input. It applies a triple barrier labeling algorithm to the input data to generate a
    meta-labeled series, which is a series of labeled events (0, 1, or -1 & 0 or 1) indicating the success or failure
    of a trade for the primary and for the secondary model. The function returns a DataFrame containing the input data and the meta-labeled series.

    """

    assert close_series.index.equals(side_series.index)

    '''Primary Model'''
    # Combine the side series with the close series
    side_labeled_ohlcv_data = pd.concat(
        [open_series, high_series, low_series, close_series, volume_series, side_series],
        axis=1, keys=['open', 'high', 'low', 'close', 'volume', 'side'])

    assert side_labeled_ohlcv_data.index.equals(close_series.index)

    # Remove Look ahead biase by lagging the signal
    side_labeled_ohlcv_data['side'] = side_labeled_ohlcv_data['side'].shift(1)  # Needed for the labeling algorythm

    # Save the raw data
    raw_data = side_labeled_ohlcv_data.copy()

    # Drop the NaN values from our data set
    side_labeled_ohlcv_data = side_labeled_ohlcv_data.dropna(axis=0, how='any', inplace=False)

    # Make sure side is an integer
    side_labeled_ohlcv_data['side'] = side_labeled_ohlcv_data['side'].astype(int)

    # Compute daily volatility
    # daily_vol = util.get_daily_vol(close=side_labeled_ohlcv_data['close'], lookback=50)
    daily_vol = side_labeled_ohlcv_data['close'].vbt.pct_change().rolling(window=50).std()

    print(f'{daily_vol = }')
    # Apply Symmetric CUSUM Filter and get timestamps for events
    # Note: Only the CUSUM filter needs a point estimate for volatility
    cusum_events = cusum_filter(side_labeled_ohlcv_data['close'], threshold=daily_vol.mean() * 0.1)
    logger.info(f'{cusum_events = }')
    if len(cusum_events) == 0:
        logger.warning('\nNo CUSUM events found with the given parameters and provided data')
        return None

    # Compute vertical barrier
    vertical_barriers = labeling.add_vertical_barrier(t_events=cusum_events, close=side_labeled_ohlcv_data['close'],
                                                      # num_days=1, num_hours=0, num_minutes=0, num_seconds=0
                                                      num_days=tbl_kwargs.get('vertical_barrier_num_days', 1),
                                                      num_hours=tbl_kwargs.get('vertical_barrier_num_hours', 0),
                                                      num_minutes=tbl_kwargs.get('vertical_barrier_num_minutes', 0),
                                                      num_seconds=tbl_kwargs.get('vertical_barrier_num_seconds', 0)
                                                      )
    logger.info(f'{vertical_barriers = }')
    triple_barrier_events = labeling.get_events(close=side_labeled_ohlcv_data['close'],
                                                side_prediction=side_labeled_ohlcv_data['side'],
                                                t_events=cusum_events,
                                                pt_sl=tbl_kwargs.get('pt_sl', [1, 1]),
                                                target=daily_vol,
                                                vertical_barrier_times=vertical_barriers,
                                                min_ret=tbl_kwargs.get('min_ret', 0.001),
                                                num_threads=tbl_kwargs.get('num_threads', 1)
                                                )

    labels = labeling.get_bins(triple_barrier_events, side_labeled_ohlcv_data['close'])

    # Shift the side series back to the original position
    raw_data.dropna(axis=0, how='any', inplace=True)
    raw_data['side'] = raw_data['side'].astype(int)

    # Nicely/properly introduce back the open,high,low, volume

    # Change raw_data side name to direction
    raw_data.rename(columns={'side': 'direction'}, inplace=True)

    labels.columns = ["ret", "target_ret", "meta_target", "prim_target"]

    returning_df = pd.concat([raw_data, labels], axis=1).fillna(0)

    # Add the first row since they were removed in the beginning after the lagging. Include dates
    first_row = {
        'open': open_series.iloc[0], 'high': high_series.iloc[0], 'low': low_series.iloc[0],
        'close': close_series.iloc[0],
        'volume': volume_series.iloc[0], 'direction': side_series.iloc[0], 'ret': 0, 'target_ret': 0, 'meta_target': 0,
        'prim_target': 0}
    first_row = pd.DataFrame(first_row, index=[close_series.index[0]])
    returning_df = pd.concat([first_row, returning_df], axis=0)  # if memory is an issue switch to dask or loop-append

    # Change prim_target and meta_target to int
    returning_df['prim_target'] = returning_df['prim_target'].astype(int)
    returning_df['meta_target'] = returning_df['meta_target'].astype(int)

    logger.info("TBL-ML-Data")
    logger.info(returning_df[["direction", "prim_target", "meta_target"]].head(10))

    # Print unique values
    unique_values = returning_df[["direction", "prim_target", "meta_target"]].apply(lambda x: x.unique())
    logger.info("Unique Values")
    logger.info(unique_values)
    # Lets show the counts of the unique values
    unique_values = returning_df[["direction", "prim_target", "meta_target"]].apply(lambda x: x.value_counts())
    logger.info("Value Counts")
    logger.info(unique_values)


    return returning_df


def save_output_data(output_data, output_file_dir, output_file_name, output_file_type, index=True):
    if isinstance(output_file_type, list):
        # This will be a self recursive function
        # assert all the elements in the list are strings
        assert all([isinstance(file_type, str) for file_type in output_file_type])
        for file_type in output_file_type:
            save_output_data(output_data, output_file_dir, output_file_name, file_type, index)
        return

    # If output_file_dir does not exist, create it
    if not output_file_dir:
        output_file_dir = "output"
    if not os.path.exists(output_file_dir):
        os.makedirs(output_file_dir)

    if "csv" in output_file_type:
        output_data.to_csv(f"{output_file_dir}/{output_file_name}.csv", index=index)
    if "pkl" in output_file_type:
        output_data.to_pickle(f"{output_file_dir}/{output_file_name}.pkl")
    if "vbt" in output_file_type:
        # output_data.to_vbt_pickle(f"{output_file_dir}/{output_file_name}.vbt")
        NotImplementedError("vbt types is not supported yet")


def compute_features_from_vbt_data(vbt_data):
    '''Create Features using TA-Lib'''
    import vectorbtpro as vbt
    features = vbt_data.run("talib_all", periods=vbt.run_func_dict(talib_mavp=14))

    # If mostly empty (features are not used) then drop the features column
    # Description describe() per column
    description = features.describe()
    logger.info(description)

    # Remove columns where mean is in [0, nan, inf, -inf] or count is 0
    columns_to_remove = []
    for column in description.columns:
        if description[column]["mean"] in [0, np.nan, np.inf, -np.inf] or description[column]["count"] == 0 or \
                description[column]["25%"] == description[column]["75%"]:
            columns_to_remove.append(column)
    features = features.drop(columns=columns_to_remove)
    logger.info(f"Removed columns: {columns_to_remove}")
    logger.info(f'{features.head(10) = }')
    return features


def flexible_tbm_labeling(
        open_series: pd.Series or vbt.Param,
        high_series: pd.Series or vbt.Param,
        low_series: pd.Series or vbt.Param,
        close_series: pd.Series or vbt.Param,
        volume_series: pd.Series or vbt.Param,
        instrument_name: str or vbt.Param, **tbl_kwargs: dict):
    print(f'{close_series = }')
    side_series = trend_scanning_labels(price_series=close_series, t_events=close_series.index,
                                        look_forward_window=20,
                                        min_sample_length=5, step=1)["bin"]
    print(f'{side_series = }')
    assert close_series.index.equals(side_series.index), "close_series and side_series must have the same index"

    triple_barrier_labeled_data = volatility_triple_barrier_label_example(
        open_series=open_series,
        high_series=high_series,
        low_series=low_series,
        close_series=close_series,
        volume_series=volume_series,
        side_series=side_series, **tbl_kwargs)


    if triple_barrier_labeled_data is None:
        logging.warning("flexible_tbm_labeling returning a None value, most likely no CUSUM events were found")
        return None

    triple_barrier_labeled_data.reset_index(inplace=True)
    triple_barrier_labeled_data.rename(columns={"index": "datetime"}, inplace=True)
    print(f'{triple_barrier_labeled_data = }')

    if tbl_kwargs.get('save_output', False):
        # Save individual data
        instrument_output_file_dir = f'{instrument_name}_{tbl_kwargs.get("output_file_name_tail", None)}'
        logging.info(f"Saving {instrument_name} data individually to {instrument_output_file_dir}")
        save_output_data(triple_barrier_labeled_data,
                         output_file_dir=tbl_kwargs.get('output_file_dir', None),
                         # output_file_name=tbl_kwargs.get('output_file_name', None),
                         output_file_name=instrument_output_file_dir,
                         output_file_type=tbl_kwargs.get('output_file_type', None),
                         index=False)

    return triple_barrier_labeled_data


def TBM_labeling(
        input_data_params: dict,
        tbl_params: dict,
        output_data_params: dict,
        **kwargs
):
    """The main script sets up input and output parameters and uses the GenieLoader module to load the input data from
    a CSV file. It then applies the example_arb_strategy (arbitrary) function to the input data to generate a labeled series.
    The labeled series and the closing price series are then passed to the daily_vol_triple_barrier_label_example
    function to generate a meta-labeled DataFrame. Finally, the script saves the meta-labeled DataFrame to an output
    file using the save_output_data function."""

    # todo should also be accepted as a parameter or at least pick up from a checkpoint like side labeled data

    # Load data and convert to a VBT compatible format for vectorized backtesting e.g. during the side labeling
    genie_loader = GenieLoader()

    from os import path
    pickle_file_path: str = input_data_params.get("pickle_file_path", '')
    if not path.isfile(pickle_file_path):
        symbols_data_obj = fetch_vbt_data(**input_data_params)
        if pickle_file_path:
            symbols_data_obj.save(pickle_file_path)
    else:
        symbols_data_obj = vbt.Data.load(pickle_file_path)

    '''Label the sides of the entries when the decision is made, not when the trade is opened -1 0 1 labeled series'''
    # side_df = example_arb_strategy(VBT_OHLCV_Data=symbols_data_obj)  # this if a strategy using VBT is used ...
    # logger.info(f'{side_df_.head(10) = }')
    # todo this needs to be passed in rather than hard coded
    # side_df = trend_scanning_labels(price_series=symbols_data_obj.close, t_events=symbols_data_obj.close.index, look_forward_window=20,
    #                                 min_sample_length=5, step=1)["bin"]

    '''Compute features from the vbt OHLCV data'''  # FIXME can be moved to another process
    # features = compute_features_from_vbt_data(symbols_data_obj) # FIXME

    """<<<<<<<<<<<<<<                          TRIPLE BARRIER Meta LABELING                            >>>>>>>>>>>>"""

    # fixme still using vbt data model
    open_df = pd.DataFrame(symbols_data_obj.open)
    open_df.columns = symbols_data_obj.symbols
    high_df = pd.DataFrame(symbols_data_obj.high)
    high_df.columns = symbols_data_obj.symbols
    low_df = pd.DataFrame(symbols_data_obj.low)
    low_df.columns = symbols_data_obj.symbols
    close_df = pd.DataFrame(symbols_data_obj.close)
    close_df.columns = symbols_data_obj.symbols
    volume_df = pd.DataFrame(symbols_data_obj.volume)
    volume_df.columns = symbols_data_obj.symbols

    # Convert
    '''Using the close and side series and other tbl configuration parameters, label --> triple barrier labeling'''

    flexible_tbm_labeling_instance = vbt.parameterized(flexible_tbm_labeling,
                                                       # merge_func="column_stack",
                                                       # n_chunks=np.floor(param_combinations.shape[pd.Series0]/4).astype(int),
                                                       chunk_len='auto',
                                                       show_progress=True,

                                                       # engine='ray', init_kwargs={
                                                       #     # 'address': 'auto',
                                                       #     'num_cpus': cpu_count() - 2,
                                                       # },

                                                       )
    # parameters = vbt.generate_param_combs((zip, close_series, side_series, symbols_data_obj.symbols))
    # todo refactor to a function
    import itertools

    open_data  =pd.DataFrame(symbols_data_obj.open).dropna()
    high_data  =pd.DataFrame(symbols_data_obj.high).dropna()
    low_data  =pd.DataFrame(symbols_data_obj.low).dropna()
    close_data  =pd.DataFrame(symbols_data_obj.close).dropna()
    volume_data  =pd.DataFrame(symbols_data_obj.volume).dropna()

    # add open high low volume
    param_configs = list(itertools.starmap(
        lambda o, h, l, c, v, i: {'open_series': o,
                                  'high_series': h,
                                  'low_series': l,
                                  'close_series': c,
                                  'volume_series': v,
                                  'instrument_name': i},
        itertools.zip_longest(
            # dataframe_to_series_list(pd.DataFrame(symbols_data_obj.open)),
            # dataframe_to_series_list(pd.DataFrame(symbols_data_obj.high)),
            # dataframe_to_series_list(pd.DataFrame(symbols_data_obj.low)),
            # dataframe_to_series_list(pd.DataFrame(symbols_data_obj.close)),
            # dataframe_to_series_list(pd.DataFrame(symbols_data_obj.volume)),

            dataframe_to_series_list(pd.DataFrame(open_data)),
            dataframe_to_series_list(pd.DataFrame(high_data)),
            dataframe_to_series_list(pd.DataFrame(low_data)),
            dataframe_to_series_list(pd.DataFrame(close_data)),
            dataframe_to_series_list(pd.DataFrame(volume_data)),

            symbols_data_obj.symbols)
    ))

    tbml_data = flexible_tbm_labeling_instance(
        param_configs=param_configs,
        **{**tbl_params, **output_data_params}
    )

    return tbml_data


if __name__ == "__main__":
    # Fixme Removed features step since is not an mvp for this module's purposes as is developed.
    # Todo unified library interface for better integration, simplicity and scalability
    """
    In this tutorial, we will build a Triple Barrier Meta Labeling pipeline using the provided functions. This pipeline 
    will take in a dataframe of historical data and return a labeled dataframe with features, primary model labels, 
    and meta labels. We will use the following functions:

    example_arb_strategy: Generates signals for entering and exiting trades based on the Bollinger Bands indicator.
    daily_vol_triple_barrier_label_example: Applies a triple barrier labeling algorithm to generate a meta-labeled 
    series.
    save_output_data: Saves the meta-labeled DataFrame to an output file.
    TBM_labeling: The main script that sets up input and output parameters and uses the other functions to generate a 
    meta-labeled DataFrame.
    
    Here's a step-by-step guide on how to use these functions:

    Define your input data parameters in the INPUT_DATA_PARAMS dictionary, including the data file directories, data 
    file names, column renaming, and more.

    Define your Triple Barrier Labeling (TBL) parameters in the TBL_PARAMS dictionary, including profit-taking and 
    stop-loss levels, minimum return, number of threads, and vertical barrier parameters.

    Define your output data parameters in the OUTPUT_DATA_PARAMS dictionary, including the output file directory, 
    output file name, and output file type.

    Call the TBM_labeling function with your input data parameters, TBL parameters, and output data parameters.

    python
    Copy code
    # Call the TBM_labeling function with the defined parameters
    labeled_data = TBM_labeling(
        input_data_params=INPUT_DATA_PARAMS,
        tbl_params=TBL_PARAMS,
        output_data_params=OUTPUT_DATA_PARAMS,
    )
    This will execute the main script that:

    Loads the input data using the GenieLoader module and converts it to a format compatible with the vectorbt library.
    Generates buy, sell, and hold signals using the example_arb_strategy function.
    Applies the triple barrier labeling algorithm to the closing price series and labeled series using the 
    daily_vol_triple_barrier_label_example function, which generates a meta-labeled DataFrame.
    Saves the meta-labeled DataFrame to an output file using the save_output_data function.
    The resulting labeled dataframe will contain the historical data along with the features, primary model labels, 
    and meta labels. This can be used as input for further analysis or machine learning models.
    """

    # todo:
    #   The biggest assumption this example makes is that your are only working with one asset and one parameter
    #       combination unlike how typically Genie is used
    #   This example also assumes working with OHLCV data, that data when passing to strategy function to label sides is
    #       prepared as a vbt.Data object, and that you want to save the output with all the columns plus the labels.
    #   Change to working with dask or vectorbt dataframes for better execution with larger datasets and more assets

    # TODO: I need to integrate into data labeling pipeline, both Vectorized/Distributed and for real-time execution
    WORKING_DIRECTORY = '/home/ruben/PycharmProjects/Genie-Trader/dev_studies_workdir'
    # ROOT_DATA_DIR = f"{WORKING_DIRECTORY}/Data/raw_data/Forex/Majors/Minute"
    ROOT_DATA_DIR = f"{WORKING_DIRECTORY}/../Data/raw_data/"
    # gET ALL DIRECTORIES RECURSIVELY
    DATA_FILE_DIRS = glob.glob(f"{ROOT_DATA_DIR}/**", recursive=True)
    print(DATA_FILE_DIRS)

    DATA_FILE_NAMES = [
        # "XAUUSD_GMT+0_NO-DST_M1.csv",
        # "US_Brent_Crude_Oil_GMT+0_NO-DST_M1.csv",
        'AAPL_1min_sample.csv',
        'BTC_1min_sample.csv',
        'ES_1min_sample.csv',
        'MSFT_1min_sample.csv',
        'QQQ_1min_sample.csv',
        'SPY_1min_sample.csv'
    ]
    OUTPUT_FILE_DIR = f"{WORKING_DIRECTORY}/tbml_output"
    OUTPUT_FILE_NAME_TAIL = "tbml_data"

    N_ROWS = 10000
    DATA_IDENTIFIER = 'M1_SampleData'
    INPUT_DATA_PARAMS = dict(
        # todo this will be changed as needed for the endpoint to save the data e.g. S3-bucket
        # todo maybe i would like to also allow for data to be loaded from an exchange api
        data_file_dirs=DATA_FILE_DIRS,
        data_file_names=DATA_FILE_NAMES,
        rename_columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Tick volume": "volume"},
        scheduler='threads',
        first_or_last='first',
        n_rows=N_ROWS,
        pickle_file_path=f"{WORKING_DIRECTORY}/{DATA_IDENTIFIER}_{N_ROWS}_data_temp.pkl",
        # if exists, then load from pickle file instead, else will create it
    )
    TBL_PARAMS = dict(
        pt_sl=[1, 1],
        min_ret=0.00001,  # todo allow user to pass a str of a function to be applied to the data to calculate this
        num_threads=28,
        #
        #  Number of D/H/m/s to add for vertical barrier
        vertical_barrier_num_days=0,
        vertical_barrier_num_hours=0,
        vertical_barrier_num_minutes=0,
        vertical_barrier_num_seconds=0,
    )
    OUTPUT_DATA_PARAMS = dict(
        # todo this will be changed as needed for the endpoint to save the data e.g. S3-bucket
        output_file_dir=OUTPUT_FILE_DIR,
        output_file_name_tail=OUTPUT_FILE_NAME_TAIL,
        save_output=True,
        output_file_type=[
            "csv",
            # "pkl"
        ],  # can be csv, pickle, vbt, or list of these
    )

    # %%%%%%%%%%%%--START-EXECUTION--%%%%%%%%%%%%
    TBM_labeling(
        input_data_params=INPUT_DATA_PARAMS,
        tbl_params=TBL_PARAMS,
        output_data_params=OUTPUT_DATA_PARAMS,
    )
    # %%%%%%%%%%%--END-OF-EXECUTION--%%%%%%%%%%%
