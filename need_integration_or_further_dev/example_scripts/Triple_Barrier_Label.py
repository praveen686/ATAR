import os.path

import numpy as np
import pandas as pd

from need_integration_or_further_dev.Standard_Algorythms import util
from need_integration_or_further_dev.Standard_Algorythms.labeling_algorythms import labeling
from need_integration_or_further_dev.Standard_Algorythms.timeseries_algorythms import timeseries_filters
from need_integration_or_further_dev.example_scripts.tbl_help import train_model, load_primary_n_meta_model_pickles, \
    save_primary_n_meta_model_pickles, live_execution_of_models
from need_integration_or_further_dev.old_modules.genie_loader import Genie_Loader


def sample_triple_barrier_strat_labeling(data, num_threads=1, dates=None):
    """
    This function is a sample of how to use the triple barrier labeling algorythm
    Step 1: Create a Genie_Loader object
    Step 2: Use the fetch_data method to get the data
    Step 3: Use the triple_barrier_labeling method to get the labels
    Step 4: Use the timeseries_tilters method to get the filtered data
    Step 5: Use the labeling method to get the labels
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
    fast_mavg = data["close"].rolling(window=fast_window, min_periods=fast_window, center=False).mean()
    slow_mavg = data["close"].rolling(window=slow_window, min_periods=slow_window, center=False).mean()
    # SUMCON_indicator = vbt.IF.from_techcon("SUMCON")
    # indicator_bs = SUMCON_indicator.run(
    #     open=data["open"],
    #     high=data["high"],
    #     low=data["low"],
    #     close=data["close"],
    #     volume=data["volume"],
    #     smooth=30
    # )
    # SUMCON_result = indicator_bs.buy - indicator_bs.sell

    '''Compile Structure and Run Master Indicator'''
    # Compute sides
    # long_signals = Master_Indicator.long_entries.values & (SUMCON_result > 0.05)
    # short_signals = Master_Indicator.short_entries.values & (SUMCON_result < -0.05)
    data['side'] = np.nan

    long_signals = fast_mavg >= slow_mavg
    short_signals = fast_mavg < slow_mavg
    # long_signals = (SUMCON_result > 0.05)
    # short_signals = (SUMCON_result < -0.05)
    data['side'] = 0
    data.loc[long_signals, 'side'] = 1
    data.loc[short_signals, 'side'] = -1

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
    STATIC_FEATURES = None#[{"id": "XAUUSD", "type": "commodity", "currency": "USD"}]
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

        triple_barrier_labeled_data = sample_triple_barrier_strat_labeling(symbols_data,
                                                                           num_threads=NUM_THREADS_FOR_TBL, dates=DATES)

        # Save triple_barrier_labeled_data
        triple_barrier_labeled_data.to_csv(os.path.join(DATA_FILE_DIR, TBL_DATA_OUTPUT))
    else:
        # Load Results
        triple_barrier_labeled_data = Genie_Loader().fetch_csv_data_dask(data_file_name=TBL_DATA_OUTPUT, data_file_dir=DATA_FILE_DIR,
                                                          scheduler='threads', n_rows=None, first_or_last='first')

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
