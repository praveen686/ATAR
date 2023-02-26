import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

from need_integration_or_further_dev.Models_practice.AutoGluon.autogluon_help import preprocess_data, split_data, \
    get_timeseries_predictor, plot_predictions

if __name__ == "__main__":
    LOAD_MODEL = False
    PREDICTION_LENGTH = 7
    TRAINING_TIME_LIMIT = 240
    TRAIN_TEST_DATA_SPLIT = 0.8

    raw_data_frame = pd.read_csv("../../../Data/XAUUSD.csv", index_col=None, parse_dates=["Datetime"])
    # todo: the preprocess_data function below can be broken down into smaller functions for more flexibility and functionality
    ts_dataframe = preprocess_data(raw_data_frame, prediction_length=PREDICTION_LENGTH)

    # todo splitdata can use the autogluon splitter or sklearn splitter instead of this simple one below
    train_data, test_data = split_data(ts_dataframe=ts_dataframe, train_test_data_split=TRAIN_TEST_DATA_SPLIT)

    # from autogluon.timeseries.splitter import MultiWindowSplitter
    #
    # splitter = MultiWindowSplitter(num_windows=5)
    # _, test_data_multi_window = splitter.split(test_data, PREDICTION_LENGTH)

    predictor = get_timeseries_predictor(load_model=LOAD_MODEL, prediction_length=PREDICTION_LENGTH)
    predictor.fit(train_data, presets="medium_quality", time_limit=TRAINING_TIME_LIMIT, num_gpus=1, )
    predictor.save()
    predictor_summary = predictor.fit_summary()
    predictor_leaderboard = predictor.leaderboard()
    print(predictor_summary)
    print(predictor_leaderboard)

    predictions = predictor.predict(test_data, num_gpu=1,  # known_covariates=future_known_covariates
                                    )
    print(predictions.head())

    # Plot the predictions
    plot_predictions(predictions=predictions, ts_dataframe=ts_dataframe, raw_data_frame=raw_data_frame,
                     train_test_data_split=TRAIN_TEST_DATA_SPLIT)
