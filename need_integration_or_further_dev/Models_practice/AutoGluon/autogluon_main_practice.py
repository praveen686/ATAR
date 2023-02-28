import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

from need_integration_or_further_dev.Models_practice.AutoGluon.autogluon_help import prepare_autogluon_data, split_data, \
    get_timeseries_predictor, plot_predictions

if __name__ == "__main__":
    LOAD_MODEL = False
    PREDICTION_LENGTH = 1
    TRAINING_TIME_LIMIT = 120
    TRAIN_TEST_DATA_SPLIT = 0.8

    X_COLUMN_NAMES = ["Open", "Low", "High"]
    ID_COLUMN_NAME = "id"
    TIMESTAMP_COLUMN_NAME = "Datetime"
    TARGET_COLUMN_NAME = "Close"
    STATIC_FEATURES = None
    WINDOW_SIZE = 100


    raw_data_frame = pd.read_csv("../../../Data/XAUUSD.csv", index_col=None, parse_dates=["Datetime"])

    # change "Tick volume" to Volume not inplace
    raw_data_frame = raw_data_frame.rename(columns={"Tick volume": "Volume"})

    # todo: the preprocess_data function below can be broken down into smaller functions for more flexibility and functionality
    ts_dataframe = prepare_autogluon_data(df=raw_data_frame, X_column_names=X_COLUMN_NAMES,
                                          target_column_name=TARGET_COLUMN_NAME, id_column_name=ID_COLUMN_NAME,
                                          timestamp_column_name=TIMESTAMP_COLUMN_NAME, static_features=STATIC_FEATURES,
                                          window_size=WINDOW_SIZE,)

    from autogluon.timeseries.splitter import MultiWindowSplitter

    splitter = MultiWindowSplitter(num_windows=5)

    # todo splitdata can use the autogluon splitter or sklearn splitter instead of this simple one below
    train_data, test_data = split_data(ts_dataframe=ts_dataframe, train_test_data_split=TRAIN_TEST_DATA_SPLIT)

    predictor = get_timeseries_predictor(load_model=LOAD_MODEL, prediction_length=PREDICTION_LENGTH,
                                         eval_metric="MASE", ignore_time_index=True, num_gpus=1,
                                         splitter=splitter,
                                         target_column_name=TARGET_COLUMN_NAME,
                                         # known_covariates_names=["weekend"],
                                         )
    predictor.fit(
        train_data, tuning_data=None, time_limit=TRAINING_TIME_LIMIT, presets="medium_quality", hyperparameters=None,
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

    # predictions = predictor.predict(test_data, model=model,
    #
    #                                 num_samples=100,
    #
    #                                 num_gpu=1,  # known_covariates=future_known_covariates
    #                                 # model='WeightedEnsemble_L2', quantiles=[0.1, 0.5, 0.9],
    #                                 )
    # Union[autogluon.timeseries.dataset.ts_dataframe.TimeSeriesDataFrame, pandas.core.frame.DataFrame],
    # known_covariates: Optional[autogluon.timeseries.dataset.ts_dataframe.TimeSeriesDataFrame] = None,
    # model: Optional[str] = None, random_seed: Optional[int] = 123, **kwargs)
    predictions = predictor.predict(test_data, known_covariates=None, model=model, random_seed=123, num_samples=100,
                                    num_gpu=1)

    print("predictions.head()")
    print(predictions.head())
    print(predictions.index)
    print(predictions.columns)
    print(predictions.keys())
    print(predictions.shape)

    # # Plot the predictions
    # plot_predictions(predictions=predictions, ts_dataframe=ts_dataframe, raw_data_frame=raw_data_frame,
    #                  train_test_data_split=TRAIN_TEST_DATA_SPLIT)
