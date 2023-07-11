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

# Logging
import logging

import numpy as np
import pandas as pd
import vectorbtpro as vbt

from Modules.FinLab_Algorythms import util
from Modules.FinLab_Algorythms.labeling_algorythms import labeling
from Modules.FinLab_Algorythms.timeseries_algorythms import timeseries_filters
from Modules.genie_loader import Genie_Loader

logger = logging.getLogger(__name__)


def example_arb_strategy(OHLCV_Data):
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
    return side


def daily_vol_triple_barrier_label_example(close_series: pd.Series, side_series: pd.Series, **tbl_kwargs):
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


def compute_features_from_vbt_data(vbt_data):
    '''Create Features using TA-Lib'''
    import vectorbtpro as vbt
    features = vbt_data.run("talib_all", periods=vbt.run_func_dict(talib_mavp=14))

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
    print(f'{features.head(10) = }')
    return features


@vbt.parameterized(
    # merge_func="column_stack",
    # n_chunks=np.floor(param_combinations.shape[pd.Series0]/4).astype(int),
    chunk_len='auto',
    show_progress=True,
    # engine='ray', init_kwargs={
    #     # 'address': 'auto',
    #     'num_cpus': cpu_count() - 2,
    # },
)
def paralelizable_tbm_labeling(close_series, side_series, **tbl_kwargs):
    triple_barrier_labeled_data = daily_vol_triple_barrier_label_example(close_series=close_series,
                                                                         side_series=side_series,
                                                                         **tbl_kwargs)

    print("triple_barrier_labeled_data")
    print(f'{triple_barrier_labeled_data.columns = }')
    print(f'{triple_barrier_labeled_data = }')

    exit()
    '''Combine the OHLCV data triple barrier labeled data'''
    # remember the close values are the same as the close values in the symbols_data_obj, so we can drop one
    input_ohlcv_df = symbols_data_obj.get()  # todo here of multi asset implementation
    triple_barrier_labeled_data = triple_barrier_labeled_data.drop(columns=["close"]).join(
        input_ohlcv_df)  # .join(features)
    triple_barrier_labeled_data.index.names = ["Datetime"]

    # reorder the columns
    triple_barrier_labeled_data = triple_barrier_labeled_data[
        input_ohlcv_df.columns.tolist() +
        # features.columns.tolist() +
        ["prim_target", "meta_target"]
        ]
    # print all columns

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
    genie_loader = Genie_Loader()
    if input_data_params["reload_data"]:
        symbols_data_obj = genie_loader.fetch_data(**input_data_params)
        symbols_data_obj.save(input_data_params["pickle_file_path"])
    else:
        symbols_data_obj = genie_loader.load_vbt_pickle(input_data_params["pickle_file_path"])

    '''Label the sides of the entries when the decision is made, not when the trade is opened -1 0 1 labeled series'''
    side_df = example_arb_strategy(OHLCV_Data=symbols_data_obj)

    '''Compute features from the vbt OHLCV data'''  # todo can be moved to another process
    # features = compute_features_from_vbt_data(symbols_data_obj)

    """<<<<<<<<<<<<<<                          TRIPLE BARRIER Meta LABELING                            >>>>>>>>>>>>"""
    close_df = symbols_data_obj.close
    assert close_df.columns.equals(side_df.columns), "close and side series do not have the same columns"

    # Convert
    '''Using the close and side series and other tbl configuration parameters, label --> triple barrier labeling'''
    # triple_barrier_labeled_data = daily_vol_triple_barrier_label_example(close_series=close_series,
    #                                                                      side_series=side_series, **tbl_params)
    tbml_data = paralelizable_tbm_labeling(
        close_series=vbt.Param([pd.Series(close_df[i]) for i in close_df]),
        side_series=vbt.Param([pd.Series(side_df[i]) for i in side_df]),
        **tbl_params
    )
    print(f'{tbml_data = }')
    exit()
    # todo
    # # Assuming df is your DataFrame with the old MultiIndex
    # old_columns = triple_barrier_labeled_data.columns
    # # Assuming symbols_data_obj is your object with the symbols property
    # symbols = symbols_data_obj.symbols
    # # Create a dictionary to map the old columns values to the new symbols
    # # Create a new Multicolumns using the mapping
    # col_list = old_columns.tolist()
    # new_tuples = [(symbols[(i * len(symbols)) // len(col_list)],) + old_tuple[-1:] for i, old_tuple in
    #               enumerate(col_list)]
    # # Assign the new index to the DataFrame
    # triple_barrier_labeled_data.columns = new_tuples
    exit()

    return triple_barrier_labeled_data


if __name__ == "__main__":
    # Fixme Removed features step since is not an mvp for this module's purposes as is developed.
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
    DATA_DIR = "../../Data"

    INPUT_DATA_PARAMS = dict(
        # todo this will be changed as needed for the endpoint to save the data e.g. S3-bucket
        data_file_dirs=[DATA_DIR],
        data_file_names=[
            "XAUUSD.csv",
            "US_Brent_Crude_Oil_GMT+0_NO-DST_M1.csv",
        ],
        rename_columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Tick volume": "volume"},
        scheduler='threads',
        first_or_last='first',
        n_rows=10000,
        #
        pickle_file_path=f"{DATA_DIR}/data_temp.pickle",
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
        output_file_name="example_triple_barrier_labeled_data",
        output_file_type=[
            "csv",
            # "pickle"
        ],  # can be csv, pickle, vbt, or list of these
    )

    # %%%%%%%%%%%%--START-EXECUTION--%%%%%%%%%%%%
    TBM_labeling(
        input_data_params=INPUT_DATA_PARAMS,
        tbl_params=TBL_PARAMS,
        output_data_params=OUTPUT_DATA_PARAMS,
    )
    # %%%%%%%%%%%--END-OF-EXECUTION--%%%%%%%%%%%

    '''
    Here are some recommendations to improve the code:

    Modularize the code by splitting it into smaller functions or classes: This will make the code easier to understand,
     maintain, and test. You can create separate functions or classes for handling data loading, processing, and saving.
    
    Add docstrings and comments: While there are already docstrings in place for some functions, consider adding more 
    detailed docstrings and comments throughout the code to explain the purpose and functionality of each section. This 
    will make it easier for others to understand and contribute to the code.
    
    Error handling: Add more error handling to ensure that the code can handle unexpected inputs or situations 
    gracefully. For example, you can use try-except blocks to catch and handle exceptions that may occur during the 
    execution of the code.
    
    Use Python's logging module instead of print statements: Replace print statements with logging calls to provide 
    more control over the output and log levels.
    
    Remove hardcoded values and make them configurable: Instead of hardcoding values, consider using configuration 
    files or command-line arguments to make the code more flexible and easier to adapt to different use cases.
    
    Unit tests: Write unit tests to ensure the correctness of the code and prevent regressions when making changes.
    
    Optimize performance: Profile the code to find performance bottlenecks and optimize them using efficient algorithms, 
    data structures, or parallelism.
    
    Use type hints: Add type hints to your functions and variables to help with code readability and allow for better 
    linting and error checking.
    
    Here's an example of how you might start refactoring the code:
    
    import logging

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    def load_data(input_data_params: dict) -> pd.DataFrame:
        """Load input data from the specified file or source."""
        # Load data logic here
        pass
    
    def process_data(data: pd.DataFrame, tbl_params: dict) -> pd.DataFrame:
        """Apply the triple barrier labeling algorithm to the input data."""
        # Process data logic here
        pass
    
    def save_data(data: pd.DataFrame, output_data_params: dict):
        """Save the processed data to the specified output file."""
        # Save data logic here
        pass
    
    def main(input_data_params: dict, tbl_params: dict, output_data_params: dict):
        data = load_data(input_data_params)
        processed_data = process_data(data, tbl_params)
        save_data(processed_data, output_data_params)
    
    if __name__ == "__main__":
        # App_Configuration dictionaries
        input_data_params = {...}
        tbl_params = {...}
        output_data_params = {...}

    main(input_data_params, tbl_params, output_data_params)
    
    '''
