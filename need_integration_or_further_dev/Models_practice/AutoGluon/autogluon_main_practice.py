import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

from need_integration_or_further_dev.Models_practice.AutoGluon.autogluon_help import get_timeseries_predictor, \
    split_data

if __name__ == "__main__":
    LOAD_MODEL = False
    pickle_file_name = "../../Dev_Modules/Triple_Barrier_Meta_Label/triple_barrier_labeled_data.csv"
    PREDICTION_LENGTH = 1
    TRAINING_TIME_LIMIT = 3
    TRAIN_TEST_DATA_SPLIT = 0.8

    X_COLUMN_NAMES = ["open", "high", "low", "close", "volume"]
    ID_COLUMN_NAME = "id"
    TIMESTAMP_COLUMN_NAME = "Datetime"
    TARGET_COLUMN_NAME = "prim_target"
    STATIC_FEATURES = None
    KNOWN_COVARIATES_NAMES = None
    EVAL_METRIC = "MASE"

    '''Load data and convert to autogluon format'''
    raw_data_frame = pd.read_csv(pickle_file_name)
    # Reset the index column
    raw_data_frame = raw_data_frame.reset_index()

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

    # # Plot the predictions
    # plot_predictions(predictions=predictions, ts_dataframe=ts_dataframe, raw_data_frame=raw_data_frame,
    #                  train_test_data_split=TRAIN_TEST_DATA_SPLIT)
