import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

from need_integration_or_further_dev.Models_practice.AutoGluon.autogluon_help import prepare_autogluon_data, split_data, \
    get_timeseries_predictor, plot_predictions

if __name__ == "__main__":
    LOAD_MODEL = False
    PREDICTION_LENGTH = 1
    TRAINING_TIME_LIMIT = 10
    TRAIN_TEST_DATA_SPLIT = 0.8

    raw_data_frame = pd.read_csv("../../../Data/XAUUSD.csv", index_col=None, parse_dates=["Datetime"])

    # change "Tick volume" to Volume not inplace
    raw_data_frame = raw_data_frame.rename(columns={"Tick volume": "Volume"})

    # todo: the preprocess_data function below can be broken down into smaller functions for more flexibility and functionality
    ts_dataframe = prepare_autogluon_data(prediction_length=PREDICTION_LENGTH,
                                          X_df=raw_data_frame[["Datetime", "Open", "High", "Low", "Close", "Volume"]],
                                          y_df=raw_data_frame["Close"],
                                          id_column="XAUUSD",
                                          timestamp_column="Datetime",
                                          static_features=None,
                                          )

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

    model = predictor.get_model_best()

    # Internal training DataFrame used as input to `model.fit()` for each model trained in predictor.fit()`
    train_data_transformed = predictor.transform_features(model=model)
    # Internal test DataFrame used as input to `model.predict_proba()` during `predictor.predict_proba(test_data, model=model)
    test_data_transformed = predictor.transform_features('test.csv', model=model)

    predictions = predictor.predict(test_data, num_gpu=1,  # known_covariates=future_known_covariates
                                    # model='WeightedEnsemble_L2', quantiles=[0.1, 0.5, 0.9],

                                    )
    print("test_data.head()")
    print(test_data.head())
    print("predictions.head()")
    print(predictions.head())

    # # Plot the predictions
    # plot_predictions(predictions=predictions, ts_dataframe=ts_dataframe, raw_data_frame=raw_data_frame,
    #                  train_test_data_split=TRAIN_TEST_DATA_SPLIT)
