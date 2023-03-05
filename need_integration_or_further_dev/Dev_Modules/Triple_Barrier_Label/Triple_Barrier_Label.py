import os.path

import numpy as np
import pandas as pd

from need_integration_or_further_dev.Standard_Algorythms import util
from need_integration_or_further_dev.Standard_Algorythms.labeling_algorythms import labeling
from need_integration_or_further_dev.Standard_Algorythms.timeseries_algorythms import timeseries_filters
from need_integration_or_further_dev.Dev_Modules.Triple_Barrier_Label.tbl_help import train_model, \
    load_primary_n_meta_model_pickles, \
    save_primary_n_meta_model_pickles, live_execution_of_models
from need_integration_or_further_dev.old_modules.genie_loader import Genie_Loader


def deprecated_sample_triple_barrier_strat_labeling(data, num_threads=1, dates=None):
    """

    """
    # Import packages
    import numpy as np
    import vectorbtpro as vbt

    if data is None:
        raise ValueError("Data is None")
    if isinstance(data, vbt.Data):
        data = pd.DataFrame(
            {
                "close": data.close.tz_localize(None),
                "open": data.open.tz_localize(None),
                "high": data.high.tz_localize(None),
                "low": data.low.tz_localize(None),
                "volume": data.get("Tick volume").tz_localize(None),
            }
        )
    elif isinstance(data, pd.DataFrame):
        # make sure the data has the correct columns
        try:
            # data = data[["close", "open", "high", "low", "volume"]]
            data.columns = ["close", "open", "high", "low", "volume"]
        except:
            raise ValueError("Data is missing columns")
    else:
        raise ValueError("Data must be a DataFrame or vbt.Data")

    if dates is not None:
        data = data.loc[dates[0]: dates[1]]

    '''Primary Model'''
    # Compute moving averages
    fast_window = 20
    slow_window = 50

    # STRATEGY!!!!
    # fast_mavg = data["close"].rolling(window=fast_window, min_periods=fast_window, center=False).mean()
    # slow_mavg = data["close"].rolling(window=slow_window, min_periods=slow_window, center=False).mean()
    # # SUMCON_indicator = vbt.IF.from_techcon("SUMCON")
    # # indicator_bs = SUMCON_indicator.run(
    # #     open=data["open"],
    # #     high=data["high"],
    # #     low=data["low"],
    # #     close=data["close"],
    # #     volume=data["volume"],
    # #     smooth=30
    # # )
    # # SUMCON_result = indicator_bs.buy - indicator_bs.sell
    #
    # '''Compile Structure and Run Master Indicator'''
    # # Compute sides
    # # long_signals = Master_Indicator.long_entries.values & (SUMCON_result > 0.05)
    # # short_signals = Master_Indicator.short_entries.values & (SUMCON_result < -0.05)
    # data['side'] = np.nan
    #
    # long_signals = fast_mavg >= slow_mavg
    # short_signals = fast_mavg < slow_mavg
    # # long_signals = (SUMCON_result > 0.05)
    # # short_signals = (SUMCON_result < -0.05)
    # data['side'] = 0
    # data.loc[long_signals, 'side'] = 1
    # data.loc[short_signals, 'side'] = -1

    from need_integration_or_further_dev.Labeling_Strategies.Simple_MA_Cross import sample_arb_strategy
    sample_arb_strategy(data["close"], log=False)

    # Remove Look ahead biase by lagging the signal
    data['side'] = data['side'].shift(1)

    # Save the raw data
    raw_data = data.copy()

    # Drop the NaN values from our data set
    data = data.dropna(axis=0, how='any', inplace=False)

    # Compute daily volatility
    daily_vol = util.get_daily_vol(close=data['close'], lookback=50)

    # Apply Symmetric CUSUM Filter and get timestamps for events
    # Note: Only the CUSUM filter needs a point estimate for volatility
    cusum_events = timeseries_filters.cusum_filter(data['close'], threshold=daily_vol.mean() * 0.5)

    # Compute vertical barrier
    vertical_barriers = labeling.add_vertical_barrier(t_events=cusum_events, close=data['close'], num_days=1)

    pt_sl = [0.5, 1]
    min_ret = 0.0005
    triple_barrier_events = labeling.get_events(close=data['close'],
                                                t_events=cusum_events,
                                                pt_sl=pt_sl,
                                                target=daily_vol,  # * 0.1,
                                                min_ret=min_ret,
                                                num_threads=num_threads,
                                                vertical_barrier_times=vertical_barriers,
                                                side_prediction=data['side'])

    labels = labeling.get_bins(triple_barrier_events, data['close'])

    raw_data['side'] = 0
    raw_data.loc[long_signals, 'side'] = 1
    raw_data.loc[short_signals, 'side'] = -1
    raw_data.dropna(axis=0, how='any', inplace=True)
    # Change raw_data side name to direction
    raw_data.rename(columns={'side': 'direction'}, inplace=True)

    labels.columns = ["ret", "trgt", "bin", "label_side"]

    return pd.concat([raw_data, labels], axis=1).fillna(0)


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

    # Change prim_target and meta_target to int
    returning_df['prim_target'] = returning_df['prim_target'].astype(int)
    returning_df['meta_target'] = returning_df['meta_target'].astype(int)

    print("TBL-ML-Data")
    print(returning_df[["direction", "prim_target", "meta_target"]].head(10))

    # Print unique values
    unique_values = returning_df[["direction", "prim_target", "meta_target"]].apply(lambda x: x.unique())
    print(unique_values)

    return returning_df


if __name__ == '__main__':
    '''BEGINNING OF CONFIGURATIONS'''
    # DATA-RELATED CONFIGURATIONS
    DATES = ['2015-01-01', '2015-10-31']
    DATA_FILE_NAME = "XAUUSD.csv"
    DATA_FILE_DIR = "../../Data"
    TBL_DATA_OUTPUT = "XAUUSD_Triple_Barrier_Labeled_Data.csv"
    FEATURE_COLUMNS = ["open", "low", "high", "close", "volume"]

    # Model Related Configurations
    MODEL_NAME = "XAUUSD_Model"
    MODEL_META_NAME = "XAUUSD_Model_Meta"
    TRAIN_TEST_DATA_SPLIT = 0.8
    PREDICTION_LENGTH = 1
    TIME_LIMIT = 2
    STATIC_FEATURES = None  # [{"id": "XAUUSD", "type": "commodity", "currency": "USD"}]
    TIMESTAMP_COLUMN = "Datetime"
    ID_COLUMN = "XAUUSD"
    NUM_GPU = 1

    # Boolean Flags
    PREPARE_TRIPLE_LABEL_STRATEGY = False  # If True, it will prepare the data for the triple barrier labeling strategy
    FRESH_TRAIN_MODEL = True  # Requires PREPARE_TRIPLE_LABEL_STRATEGY to be True unless retraining
    SAVE_MODEL_AFTER_TRAINING = True  # Requires FRESH_TRAIN_MODEL to be True unless retraining
    #
    LIVE_EXECUTION_TEST = False
    DISPLAY_ALL_COLUMNS_N_ROWS = True

    # Multi-Processing Configurations
    NUM_THREADS_FOR_TBL = 28  # Number of threads to use for the triple barrier labeling strategy

    '''END OF CONFIGURATIONS'''

    # Configuring Aux Settings
    if DISPLAY_ALL_COLUMNS_N_ROWS:
        # display all columns and rows
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)

    # Prepare Triple Barrier Labeled Data
    if PREPARE_TRIPLE_LABEL_STRATEGY:
        symbols_data = Genie_Loader().fetch_csv_data_dask(data_file_name=DATA_FILE_NAME, data_file_dir=DATA_FILE_DIR,
                                                          scheduler='threads', n_rows=None, first_or_last='first')

        # todo compute side with strategy, waiting for pipeline to be ready

        triple_barrier_labeled_data = daily_vol_triple_barrier_label_example(close_series=close_series,
                                                                             side_series=side_series, **{
                "test_n_elements": 10_000,
                "pt_sl": [0.5, 1],
                "min_ret": 0.0005,
                "num_threads": 28,
                #
                #  Number of D/H/m/s to add for vertical barrier
                "vertical_barrier_num_days": 1,
                "vertical_barrier_num_hours": 0,
                "vertical_barrier_num_minutes": 0,
                "vertical_barrier_num_seconds": 0,
                #
            })

        # Save triple_barrier_labeled_data
        triple_barrier_labeled_data.to_csv(os.path.join(DATA_FILE_DIR, TBL_DATA_OUTPUT))
    else:
        # Load Results
        triple_barrier_labeled_data = Genie_Loader().fetch_csv_data_dask(data_file_name=TBL_DATA_OUTPUT,
                                                                         data_file_dir=DATA_FILE_DIR,
                                                                         scheduler='threads', n_rows=None,
                                                                         first_or_last='first')

    if FRESH_TRAIN_MODEL:
        # Train the model
        primary_model, meta_model = train_model(
            triple_barrier_labeled_data=triple_barrier_labeled_data,
            #
            train_test_data_split=TRAIN_TEST_DATA_SPLIT,
            prediction_length=PREDICTION_LENGTH,
            time_limit=TIME_LIMIT,
            static_features=STATIC_FEATURES,
            timestamp_column=TIMESTAMP_COLUMN,
            id_column=ID_COLUMN,
            num_gpu=NUM_GPU,
            feature_columns=FEATURE_COLUMNS,
        )

        if SAVE_MODEL_AFTER_TRAINING:
            # Save the model
            save_primary_n_meta_model_pickles(primary_model_path=f'{MODEL_NAME}.pkl',
                                              meta_model_path=f'{MODEL_META_NAME}.pkl')
    else:
        # Load the model
        primary_model, meta_model = load_primary_n_meta_model_pickles(primary_model_path=f'{MODEL_NAME}.pkl',
                                                                      meta_model_path=f'{MODEL_META_NAME}.pkl')

    if LIVE_EXECUTION_TEST:
        assert primary_model and meta_model, "Models not loaded or trained"
        for i in zip(triple_barrier_labeled_data['open'].values,
                     triple_barrier_labeled_data['low'].values,
                     triple_barrier_labeled_data['high'].values,
                     triple_barrier_labeled_data['close'].values,
                     triple_barrier_labeled_data['volume'].values):
            print(live_execution_of_models(i[0], i[1], i[2], i[3], i[4],
                                           primary_model=primary_model, meta_model=meta_model
                                           ))
