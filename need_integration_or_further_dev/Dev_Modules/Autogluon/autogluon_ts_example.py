import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor


def ag_ts_get_predictor(
        prediction_length,
        target_column_name,
        model_path,
        load_model,
        eval_metric="MASE",
        ignore_time_index=False,
        splitter="last_window",
        known_covariates_names=None,
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
        predictor = TimeSeriesPredictor.load(model_path)
    else:
        predictor = TimeSeriesPredictor(
            target=target_column_name,
            known_covariates_names=known_covariates_names,
            prediction_length=prediction_length,
            eval_metric=eval_metric,
            path=model_path,
            verbosity=4,
            quantile_levels=None,
            ignore_time_index=ignore_time_index,
            validation_splitter=splitter,
            num_gpus=num_gpus,
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

    # If id_label not in columns then we will set the id column to be the same for all rows (i.e. one asset)
    if id_label not in df.columns:
        df[id_label] = "Asset_1"

    # Convert to autogluon format
    ts_ag_dataframe = TimeSeriesDataFrame.from_data_frame(
        df,
        id_column=id_label,
        timestamp_column=timestep_label,
    )

    # If regularize_to_freq is not None then we will regularize the data to the specified frequency in order to
    #       ensure that the data is regularized to the same frequency and auto-gluon can handle it
    if regularize_to_freq is not None:
        ts_ag_dataframe = ts_ag_dataframe.to_regular_index(freq=regularize_to_freq).fill_missing_values()

    # Add Static Features
    if static_features is not None:
        ts_ag_dataframe.add_static_features(static_features).set_index(timestep_label)

    # todo here we will deal with the known covariates:
    #       Need to check whether the known covariates are in the dataframe and if not then we will add them if they
    #           are implemented by ag, us or the user and if they are not then we will raise an error.
    #       We have not worked with known covariates yet so we will leave this for now
    return ts_ag_dataframe


def ag_ts_split_data(ag_ts_dataframe, train_test_data_split):  # todo add to auto-gluon
    """
    Split Data According to Method

    slice_by_time(start_time, end_time): Select a subsequence from each time series between start (inclusive)
                                            and end (exclusive) timestamps.

    slice_by_timestep([start_index, end_index]): Select a subsequence from each time series between start (inclusive)
                                            and end (exclusive) indices.

    split_by_time(cutoff_time): Split dataframe to two different TimeSeriesDataFrame s before and after a certain
                                        cutoff_time.

    split_by_ratio(ratio): Split dataframe to two different TimeSeriesDataFrame s by a certain ratio.

    """

    # Determine method to split data based on input
    # If tuple or list then it has to be either slice_by_time or slice_by_timestep method, thus we can then narrow
    #       down based on type of elements
    if isinstance(train_test_data_split, (tuple, list)):
        #
        if isinstance(train_test_data_split[0], str):
            # If tuple or list and first element is a string then it has to be the slice_by_time method
            train_data, test_data = ag_ts_dataframe.slice_by_time(
                start_time=train_test_data_split[0],
                end_time=train_test_data_split[1],
            )
        elif isinstance(train_test_data_split[0], int):
            # If tuple or list and first element is an int then it has to be the slice_by_timestep method
            train_data, test_data = ag_ts_dataframe.slice_by_timestep(
                start_index=train_test_data_split[0],
                end_index=train_test_data_split[1],
            )
        else:
            raise ValueError("Invalid train_test_data_split input. Either tuple or list of strings or ints."
                             "Got: {}".format(train_test_data_split))
    elif isinstance(train_test_data_split, str):
        # If string then it has to be the split_by_time method
        train_data, test_data = ag_ts_dataframe.split_by_time(
            cutoff_time=train_test_data_split,
        )
    elif isinstance(train_test_data_split, float):
        # If float then it has to be the split_by_ratio method
        split_index = int(len(ag_ts_dataframe) * train_test_data_split)
        split_timestamp = ag_ts_dataframe.index[split_index][1]  # The second element = timestamp [item_id, timestamp]
        train_data, test_data = ag_ts_dataframe.split_by_time(
            cutoff_time=split_timestamp,
        )
    else:
        raise ValueError(f"Invalid train_test_data_split input. Either (tuple or list of strings or ints), a (string)"
                         f"or a (float).\n"
                         f"     Got: {train_test_data_split}")

    return train_data, test_data


if __name__ == "__main__":
    # todo:
    #  general:
    #       Add more documentation
    #       fill out kwargs for functionality and customization
    #       I do want to make a quick note that for tasks requiring training of multiple predictors, e.g. meta labels,
    #           changes are needed
    #  prediction_length:
    #       Needs to be determined based on the data
    #       Splitting needs to make sure that test data is long enough to make a prediction on since
    #           minimum len(prediction_data) >= prediction_length and for best performance, all time series should
    #           have length > 2 * prediction_length.
    #  known_covariates: (i.e. currently not used)
    #       If known_covariates_names were specified when creating the predictor, train_data [and tunning] must include
    #           the columns listed in known_covariates_names with the covariates values aligned with the target time
    #           series for both fitting and predicting . The known covariates must have a numeric (float or integer)
    #           dtype.
    #       Needs checking throughout the code to make sure that the data is present and in the correct format
    #       Needs method to label, e.g. weekends, holidays, etc.
    #       Needs to be split along with train and test data
    #       Currently needs to be passed in with the input data, but certain features can be added to the data
    #           automatically such as weekends, holidays, etc. since these are known and pretty standard
    #  static_features:
    #       Has not gotten any work done on it yet
    #       These do not vary over time and are used to add additional information to the model
    #  MultiWindowSplitter:
    #       Needs to be implemented
    #  Hyperparameter Tuning:
    #       Needs to be implemented if we dont want to just run the default models or settings

    EQUIPMENT_PARAMS = dict(
        NUMBER_OF_CPUS=28,
        NUMBER_OF_GPUS=1
    )

    LOAD_DATA_PARAMS = dict(
        csv_file_path="../../../Data/sample_triple_barrier_labeled_data.csv",
    )

    PREPROCESS_PARAMS = dict(
        df=pd.read_csv(LOAD_DATA_PARAMS["csv_file_path"]).drop(columns=["meta_target"]),
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
        train_test_data_split=0.9,
    )
    PREDICTOR_PARAMS = dict(
        prediction_length=1440 * 7,
        target_column_name="prim_target",
        model_path="XAUUSD_Primary_Model_BBANDS_1min",
        load_model=False,
        eval_metric="sMAPE",
        # splitter="multi_window",
        splitter="last_window",

        ignore_time_index=False,
        known_covariates_names=None,  # todo currently not used or implemented
    )
    FIT_PARAMS = dict(
        time_limit=1800,
        presets="best_quality",
        feature_metadata='infer',
        infer_limit=None,
        infer_limit_batch_size=None,
        fit_weighted_ensemble=True,
        num_cpus=EQUIPMENT_PARAMS["NUMBER_OF_CPUS"],
        num_gpus=EQUIPMENT_PARAMS["NUMBER_OF_GPUS"],
        # hyperparameters=None,
    )
    PREDICTION_PARAMS = dict(
        num_cpus=EQUIPMENT_PARAMS["NUMBER_OF_CPUS"],
        num_gpus=EQUIPMENT_PARAMS["NUMBER_OF_GPUS"],
        random_seed=123,
        # known_covariates=None,  # todo include it in the input date if known_covariates_names was set
    )

    '''Load data and convert to autogluon format'''
    ts_dataframe = ag_ts_preprocess(**PREPROCESS_PARAMS)
    print("AG Prepared Data")
    print(ts_dataframe)

    '''Split data into train and test'''
    train_data, test_data = ag_ts_split_data(ag_ts_dataframe=ts_dataframe, **SPLIT_DATA_PARAMS)
    print("Training Data")
    print(train_data)
    print("Test Data")
    print(test_data)

    '''Create Predictor and fit model'''
    predictor = ag_ts_get_predictor(**PREDICTOR_PARAMS)
    predictor.fit(train_data=train_data, tuning_data=None, show_plot=True, plot=True, verbosity=4, **FIT_PARAMS)
    predictor.fit_summary(verbosity=2)
    predictor.save()

    '''Predict'''
    model = predictor.get_model_best()
    predictions = predictor.predict(data=test_data, model=model, **PREDICTION_PARAMS)

    print("Predictions")
    print(predictions)
