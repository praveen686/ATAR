# Outputs from Genie __> [R parameters] * [Sim Metrics "Features"]
# Currently this module assumes that only one asset
# Wanted to have parameter sensitivity report and tbl trained model done here but will split and later on combine into
#   another pipeline which makes better use of resources and the flow of operations like backtests
#   Thus here the ag model is trained on what is believed to be the optimal parameter combinations (which are passed)
#   For now only one parameter combination and asset are used (will be expanded on) and will not optimize

"""Summary:
    ag = autogluon
::
"""
import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame

from need_integration_or_further_dev.Dev_Modules.Autogluon.autogluon_ts_example import get_timeseries_predictor, \
    split_data
from need_integration_or_further_dev.Dev_Modules.Triple_Barrier_Label.tbl_functions import \
    daily_vol_triple_barrier_label_example
from need_integration_or_further_dev.Dev_Modules.genie_loader import Genie_Loader
from need_integration_or_further_dev.Labeling_Strategies.sample_arb_strategy import sample_arb_strategy


# todo class or function ...

def tbl_mai():
    '''Load data and convert to a VBT compatible format for vectorized backtesting e.g. during the side labeling'''
    genie_loader = Genie_Loader()
    if RELOAD_DATA:
        symbols_data_obj = genie_loader.fetch_data(data_file_names=data_file_names, data_file_dirs=data_file_dirs,
                                                   rename_columns={"Open": "open", "High": "high", "Low": "low",
                                                                   "Close": "close", "Tick volume": "volume"})
        symbols_data_obj.save(pickle_file_name)
    else:
        symbols_data_obj = genie_loader.load_vbt_pickle(pickle_file_name)

    '''Label the sides of the entries when the decision is made, not when the trade is opened -1 0 1 labeled series'''
    side_df = sample_arb_strategy(
        OHLCV_Data=symbols_data_obj,
        R_parameters={},
        # todo make sure to pass inputs as a dict/json of parameter values to the function
        **{}
    )

    '''todo: This is a hotfix due to only working with one asset at the moment'''
    close_series = symbols_data_obj.close  # needs to be only one asset otherwise dimensionality error in multiindex
    side_series = side_df[side_df.keys()[0]]

    '''Using the close and side series and other tbl configuration parameters, label --> triple barrier labeling'''
    triple_barrier_labeled_data = daily_vol_triple_barrier_label_example(close_series=close_series,
                                                                         side_series=side_series, **tbl_kwargs)

    '''Combine the OHLCV data triple barrier labeled data'''
    # remember the close values are the same as the close values in the symbols_data_obj so we can drop one
    input_ohlcv_df = symbols_data_obj.get()
    triple_barrier_labeled_data = triple_barrier_labeled_data.drop(columns=["close"]).join(input_ohlcv_df)
    triple_barrier_labeled_data.index.names = ["Datetime"]

    triple_barrier_labeled_data = triple_barrier_labeled_data[
        input_ohlcv_df.columns.tolist() + ["prim_target", "meta_target"]]
    print(triple_barrier_labeled_data.head())

    '''Save the triple barrier labeled data to be used in other processes'''
    triple_barrier_labeled_data.to_csv("triple_barrier_labeled_data.csv", )
    triple_barrier_labeled_data.to_pickle("triple_barrier_labeled_data.pickle")

    return triple_barrier_labeled_data


if __name__ == "__main__":
    RELOAD_DATA = False
    # TBL-ML-PARAMETERS
    data_file_names = ["XAUUSD.csv"]
    data_file_dirs = ["../../../Data"]
    pickle_file_name = "XAUUSD.pickle"
    tbl_kwargs = {
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
    }

    # AUTOGLUON PARAMETERS
    LOAD_MODEL = False
    PREDICTION_LENGTH = 10
    TRAINING_TIME_LIMIT = 3
    TRAIN_TEST_DATA_SPLIT = 0.8
    X_COLUMN_NAMES = ["open", "high", "low", "close", "volume"]
    ID_COLUMN_NAME = "id"
    TIMESTAMP_COLUMN_NAME = "Datetime"
    TARGET_COLUMN_NAME = "prim_target"
    STATIC_FEATURES = None
    KNOWN_COVARIATES_NAMES = None
    EVAL_METRIC = "MASE"

    triple_barrier_labeled_data = tbl_mai()

    """AUTOGLUON"""
    # Reset the index column
    raw_data_frame = triple_barrier_labeled_data.reset_index()

    # Convert Datetime column to datetime64[ns] type with no timezone
    raw_data_frame["Datetime"] = pd.to_datetime(raw_data_frame["Datetime"], utc=True).dt.tz_convert(None)

    # Since this is just one asset and this is a time series, we can set the id column to be the same for all rows
    raw_data_frame["id"] = "XAUUSD"

    # Convert to autogluon format
    ts_dataframe = TimeSeriesDataFrame.from_data_frame(
        raw_data_frame,
        id_column=ID_COLUMN_NAME,
        timestamp_column=TIMESTAMP_COLUMN_NAME,
    ).to_regular_index(freq="min").fill_missing_values()

    # # Hotfix for autogluon bug
    # ts_dataframe._cached_freq = "min"

    if STATIC_FEATURES:
        # add static features
        ts_dataframe.static_features = pd.DataFrame(
            # data=[{"id": "XAUUSD", "type": "commodity", "currency": "USD"}],
            data=STATIC_FEATURES,
        ).set_index("id")

    print("ts_dataframe.head()")
    print(ts_dataframe.head())

    '''Split data into train and test'''
    # todo splitdata can use the autogluon splitter or sklearn splitter instead of this simple one below
    train_data, test_data = split_data(ts_dataframe=ts_dataframe, train_test_data_split=TRAIN_TEST_DATA_SPLIT)

    predictor = get_timeseries_predictor(
        prediction_length=PREDICTION_LENGTH,
        target_column_name=TARGET_COLUMN_NAME,
        model_path="ag_model",
        load_model=LOAD_MODEL,
        eval_metric=EVAL_METRIC,
        ignore_time_index=False,
        splitter="last_window",
        known_covariates_names=KNOWN_COVARIATES_NAMES,
        num_gpus=0,
    )
    predictor.fit(
        train_data, tuning_data=None, time_limit=TRAINING_TIME_LIMIT, presets="fast_training", hyperparameters=None,
        feature_metadata='infer', infer_limit=None, infer_limit_batch_size=None, fit_weighted_ensemble=True,
        num_cpus='auto', num_gpus='auto'
    )
    predictor.save()
    predictor_summary = predictor.fit_summary()
    predictor_leaderboard = predictor.leaderboard()
    print(predictor_summary)
    print(predictor_leaderboard)

    model = predictor.get_model_best()

    print("test_data.head()")
    print(test_data.head())
    print(test_data.index)
    print(test_data.columns)
    print(test_data.keys())
    print(test_data.shape)

    predictions = predictor.predict(test_data, known_covariates=None, model=model, random_seed=123, num_samples=100,
                                    num_gpu=1)

    print("predictions.head()")
    print(predictions.head())

    # plot previous data and predictions
    plot_data = test_data.copy()
    plot_data["prediction_lower"] = predictions.quantile(0.025, axis=1)
    plot_data["prediction_upper"] = predictions.quantile(0.975, axis=1)
    plot_data["prediction_mean"] = predictions.mean(axis=1)
    plot_data["prediction_std"] = predictions.std(axis=1)

    #plot
    import matplotlib.pyplot as plt
    plt.figure(figsize=(20, 10))
    plt.plot(plot_data["prediction_mean"], label="prediction_mean")
    plt.plot(plot_data["prediction_lower"], label="prediction_lower")
    plt.plot(plot_data["prediction_upper"], label="prediction_upper")
    plt.plot(plot_data["prim_target"], label="prim_target")
    plt.legend()
    plt.show()
