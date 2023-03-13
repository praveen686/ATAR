import pandas as pd
from autogluon.core import space, TabularDataset
from autogluon.features import AutoMLPipelineFeatureGenerator
from autogluon.tabular import TabularPredictor, TabularDataset

from need_integration_or_further_dev.Dev_Modules.genie_loader import Genie_Loader


# todo This is still being changed from the original ts example

def ag_ts_get_predictor(
        prediction_length,
        target_column_name,
        model_path,
        load_model,
        eval_metric="MASE",
        ignore_time_index=False,
        splitter="last_window",
        known_covariates_names=None,
        quantile_levels=None,
        num_gpus=1
):
    """
    AutoGluon TimeSeriesPredictor predicts future values of multiple related time series.

    TimeSeriesPredictor provides probabilistic (distributional) multi-step-ahead forecasts for univariate time series.
    The forecast includes both the mean (i.e., conditional expectation of future values given the past), as well as
    the quantiles of the forecast distribution, indicating the range of possible future outcomes.

    TimeSeriesPredictor fits BOTH “global” deep learning models that are shared across all time series
    (e.g., DeepAR, Transformer), and “local” statistical models that are fit to each individual time series
    (e.g., ARIMA, ETS).

    TimeSeriesPredictor expects input data and makes predictions in the TimeSeriesDataFrame format.
    """

    if load_model:
        predictor = TabularPredictor.load(model_path)
    else:
        predictor = TabularPredictor(
            target=target_column_name,
            known_covariates_names=known_covariates_names,
            prediction_length=prediction_length,
            eval_metric=eval_metric,
            path=model_path,
            verbosity=4,
            ignore_time_index=ignore_time_index,
            validation_splitter=splitter,
            num_gpus=num_gpus,
            quantile_levels=quantile_levels,
        )

    return predictor


def ag_ts_preprocess(df: pd.DataFrame, timestep_label, id_label, static_features=None,
                     regularize_to_freq="min",
                     ):
    """Construct a TimeSeriesDataFrame from a DataFrame"""

    # If timestep label not in columns then we will reset the index and expect the index to be a DatetimeIndex with
    #       the same label as the timestep_label
    if timestep_label not in df.columns:
        # Reset the index column
        df = df.reset_index()
    # Convert Datetime column to datetime64[ns] type with no timezone
    df[timestep_label] = pd.to_datetime(df[timestep_label], utc=True).dt.tz_convert(None)

    # Convert to autogluon format
    ts_ag_dataframe = TabularDataset(df)

    return ts_ag_dataframe


if __name__ == "__main__":
    # todo:
    #  general:
    #       ...

    LOAD_MODEL = False
    EQUIPMENT_PARAMS = dict(
        NUMBER_OF_CPUS=28,
        NUMBER_OF_GPUS=1
    )

    LOAD_DATA_PARAMS = dict(
        csv_file_path="../../../Data/sample_triple_barrier_labeled_data.csv",
        # csv_file_path="../../../Data/sample_triple_barrier_labeled_data_1.csv",
    )
    genie_loader = Genie_Loader()

    PREPROCESS_PARAMS = dict(
        # df=pd.read_csv(LOAD_DATA_PARAMS["csv_file_path"]).drop(columns=["meta_target"]),
        df=pd.read_csv(LOAD_DATA_PARAMS["csv_file_path"]).drop(columns=["meta_target"]),
        # df=pd.read_csv(LOAD_DATA_PARAMS["csv_file_path"]),
        timestep_label="Datetime",
        id_label="id",
        static_features=None,
        regularize_to_freq="min"
        #
        # todo here will be the kwargs for covariates, etc... to be used in the preprocessing, splitting, and modeling
    )
    SPLIT_DATA_PARAMS = dict(
        # train_test_data_split="2019-01-01 00:00:00",
        # train_test_data_split=(0, 1000),
        train_test_data_split=0.8,
    )
    PREDICTOR_PARAMS = dict(
        prediction_length=60,
        target_column_name="prim_target",
        model_path="XAUUSD_Primary_Model_BBANDS_1min_tabular",
        # target_column_name="meta_target",
        # model_path="XAUUSD_Meta_Model_BBANDS_1min",
        #
        load_model=LOAD_MODEL,
        eval_metric="sMAPE",
        # splitter="multi_window",
        splitter="last_window",
        quantile_levels=[0.1, 0.5, 0.75, 0.85, 0.95],

        ignore_time_index=False,
        known_covariates_names=None,  # todo currently not used or implemented
    )
    FIT_PARAMS = dict(
        time_limit=1800,
        # presets="fast_training",
        presets="medium_quality",
        # presets="high_quality",
        feature_metadata='infer',
        infer_limit=None,
        infer_limit_batch_size=None,
        fit_weighted_ensemble=True,

        # hyperparameters={
        #     "Naive": {'ag_args_fit': {'num_gpus': 1, 'num_cpus': 28}},
        #     "SeasonalNaive": {'ag_args_fit': {'num_gpus': 1, 'num_cpus': 28}},
        #     "ARIMA": {'ag_args_fit': {'num_gpus': 1, 'num_cpus': 28}},
        #     # "ETS": {'ag_args_fit': {'num_gpus': 1, 'num_cpus': 28}},
        #     "Theta": {'ag_args_fit': {'num_gpus': 1, 'num_cpus': 28}},
        #     "AutoETS": {'ag_args_fit': {'num_gpus': 1, 'num_cpus': 28}},
        #     "AutoARIMA": {'ag_args_fit': {'num_gpus': 1, 'num_cpus': 28}},
        #     # "AutoGluonTabular": {'ag_args_fit': {'num_gpus': 1, 'num_cpus': 28}},
        #     # "DeepAR": {'ag_args_fit': {'num_gpus': 1, 'num_cpus': 28}},
        #     # "SimpleFeedForward": {'ag_args_fit': {'num_gpus': 1, 'num_cpus': 28}},
        #     # "TemporalFusionTransformer": {'ag_args_fit': {'num_gpus': 1, 'num_cpus': 28}},
        # },

        num_cpus=EQUIPMENT_PARAMS["NUMBER_OF_CPUS"],
        num_gpus=EQUIPMENT_PARAMS["NUMBER_OF_GPUS"],

        # hyperparameters=None,
    )
    PREDICTION_PARAMS = dict(
        num_cpus=EQUIPMENT_PARAMS["NUMBER_OF_CPUS"],
        num_gpus=EQUIPMENT_PARAMS["NUMBER_OF_GPUS"],
        random_seed=None,
        # known_covariates=None,  # todo include it in the input date if known_covariates_names was set
    )

    '''Load data and convert to autogluon format'''
    ts_dataframe = ag_ts_preprocess(**PREPROCESS_PARAMS)
    print("AG Prepared Data")
    print(ts_dataframe)

    '''Split data into train and test'''
    # train_data, test_data = ag_ts_split_data(ag_ts_dataframe=ts_dataframe, **SPLIT_DATA_PARAMS)
    # print("Training Data")
    # print(train_data)
    # print("Test Data")
    # print(test_data)
    train_data = ts_dataframe.sample(frac=0.8, random_state=1)
    test_data = ts_dataframe.sample(frac=0.2, random_state=1)
    print(train_data)
    print(test_data)

    '''Create Predictor and fit model'''
    # predictor = ag_ts_get_predictor(**PREDICTOR_PARAMS)
    #
    # # if PREDICTION_PARAMS["load_model"]:
    # if not LOAD_MODEL:
    #     predictor.fit(train_data=train_data, tuning_data=test_data, verbosity=4,
    #                   **FIT_PARAMS)
    #     predictor.save()
    #
    # predictor.fit_summary(verbosity=2)
    #
    # '''Predict'''
    # model = predictor.get_model_best()
    # predictions = predictor.predict(data=test_data, model=model, **PREDICTION_PARAMS)

    # Fit predictor

    # Generate new features
    feature_generator = AutoMLPipelineFeatureGenerator()
    feature_generator.fit(train_data, label=PREDICTOR_PARAMS["target_column_name"])
    train_data_transformed = feature_generator.transform(train_data)
    test_data_transformed = feature_generator.transform(test_data)
    print(train_data_transformed.head())
    print(train_data_transformed.columns)

    # Combine features and target
    train_data_transformed[PREDICTOR_PARAMS["target_column_name"]] = train_data[PREDICTOR_PARAMS["target_column_name"]]
    test_data_transformed[PREDICTOR_PARAMS["target_column_name"]] = test_data[PREDICTOR_PARAMS["target_column_name"]]
    print(train_data_transformed.head())
    print(train_data_transformed.columns)

    if not LOAD_MODEL:
        # Fit predictor on transformed data
        predictor = TabularPredictor(label=PREDICTOR_PARAMS["target_column_name"],
                                     problem_type=None,
                                     eval_metric=None,
                                     path="AutogluonModels",
                                     verbosity=4,
                                     sample_weight=None,
                                     weight_evaluation=False,
                                     groups=None,
                                     )
        predictor.fit(
            train_data=train_data_transformed,
            tuning_data=test_data_transformed,
            use_bag_holdout=True,
            time_limit=36000,
            presets="best_quality",
            hyperparameters=None,
            feature_metadata='infer',
            infer_limit=None,
            infer_limit_batch_size=None,
            fit_weighted_ensemble=True,
            num_cpus=28,
            num_gpus=1,
        )

        # Evaluate predictor on transformed data
        leaderboard = predictor.leaderboard(test_data_transformed, silent=True)
        print(leaderboard)

        # # Save predictor
        predictor.save()
    else:
        # Load predictor
        predictor = TabularPredictor.load("AutogluonModels")
        predictor.fit_extra(train_data=train_data_transformed,
            tuning_data=test_data_transformed,
            use_bag_holdout=True,
            time_limit=36000,
            presets="best_quality",
            hyperparameters=None,
            feature_metadata='infer',
            infer_limit=None,
            infer_limit_batch_size=None,
            fit_weighted_ensemble=True,
            num_cpus=28,
            num_gpus=1,)

    # Make predictions
    y_pred = predictor.predict(test_data_transformed)
    print("test_data_transformed")
    # print(test_data_transformed[PREDICTOR_PARAMS["target_column_name"]].value_counts())
    print(test_data_transformed[PREDICTOR_PARAMS["target_column_name"]].sum())
    print("y_pred.value_counts()")
    # count per value
    print(y_pred.value_counts())

    # Make predictions on new data with raw input and return both prediction and probabilities
    test_data_unlabeled = test_data_transformed.drop(labels=[PREDICTOR_PARAMS["target_column_name"]], axis=1)
    y_pred_proba = predictor.predict_proba(test_data_unlabeled)

    print("y_pred_proba")
    print(y_pred_proba)

    # '''Plot predictions'''
    # import plotly.graph_objects as go
    # import plotly.express as px
    # import plotly.io as pio
    #
    # pio.renderers.default = "browser"
    #
    # fig = go.Figure()
    # # make sure to include the test data as well to see if the predictions are correct
    # fig.add_trace(go.Scatter(x=test_data.index.get_level_values(1), y=test_data["prim_target"], name="Test Data"))
    # # fig.add_trace(go.Scatter(x=predictions.index.get_level_values(1), y=predictions["0.95"], name="Predictions 0.95"))
    # # fig.add_trace(go.Scatter(x=predictions.index.get_level_values(1), y=predictions["0.85"], name="Predictions 0.85"))
    # # fig.add_trace(go.Scatter(x=predictions.index.get_level_values(1), y=predictions["0.75"], name="Predictions 0.75"))
    # # fig.add_trace(go.Scatter(x=predictions.index.get_level_values(1), y=predictions["0.5"], name="Predictions 0.5"))
    # # fig.add_trace(go.Scatter(x=predictions.index.get_level_values(1), y=predictions["0.1"], name="Predictions 0.1"))
    # fig.show()
