import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor


def prepare_autogluon_data(
        df,
        id_column_name,
        timestamp_column_name,
        X_column_names,
        target_column_name,
        static_features=None,
        window_size=100,
):  # todo generalize this function
    # add id column and target column
    # raw_data_frame = X_df.copy()
    # raw_data_frame['id'] = id_column
    # raw_data_frame['target'] = y_df

    # raw_data_frame = df[[id_column_name, timestamp_column_name] + X_column_names + [target_column_name]]
    raw_data_frame = df[[timestamp_column_name] + X_column_names + [target_column_name]]

    # drop NaNs
    clean_data_frame = raw_data_frame.dropna()


    if id_column_name not in clean_data_frame.columns:
        # Add an id column to the data frame to split the data into multiple time series of size window_size
        # e.g. if window_size=100, then the first 100 rows will be one time series, the next 100 rows will be another time series, etc.
        clean_data_frame[id_column_name] = clean_data_frame.index // window_size
        print(clean_data_frame.head())
        print(clean_data_frame.tail())

    # create TimeSeriesDataFrame
    ts_dataframe = TimeSeriesDataFrame.from_data_frame(
        clean_data_frame,
        id_column=id_column_name,
        timestamp_column=timestamp_column_name,
    )

    if static_features:
        # add static features
        ts_dataframe.static_features = pd.DataFrame(
            # data=[{"id": "XAUUSD", "type": "commodity", "currency": "USD"}],
            data=static_features,
        ).set_index("id")

    return ts_dataframe


def split_data(ts_dataframe, train_test_data_split):
    # train_data, test_data = ts_dataframe.split_before(train_test_data_split)
    # return train_data, test_data
    # Split the data into train and test 80 and 20
    train_data = ts_dataframe.iloc[:int(len(ts_dataframe) * train_test_data_split)]
    test_data = ts_dataframe.iloc[int(len(ts_dataframe) * train_test_data_split):]
    return train_data, test_data


def get_timeseries_predictor(
        load_model,
        prediction_length,
        target_column_name,
        eval_metric="MASE",
        ignore_time_index=False,
        num_gpus=0,
        splitter="last_window",
        # known_covariates_names=["weekend"],

):
    if load_model:
        predictor = TimeSeriesPredictor.load("model")
    else:

        predictor = TimeSeriesPredictor(
            target=target_column_name,
            known_covariates_names=None,
            prediction_length=prediction_length,
            eval_metric=eval_metric,
            path="model",
            verbosity=2,
            quantile_levels=None,
            ignore_time_index=ignore_time_index,
            validation_splitter=splitter,
            num_gpus=num_gpus,
        )

    return predictor


def plot_predictions(predictions, ts_dataframe, raw_data_frame, train_test_data_split):
    def add_plot(df, title):
        from matplotlib import pyplot as plt
        plt.figure(figsize=(12, 6))
        # Plot all columns and label them with their name
        for col in df.columns:
            plt.plot(df[col].values, label=col)
        plt.legend()
        plt.title(title)
        plt.show()

    print("raw_data_frame.head()")
    print(raw_data_frame.head())
    print("ts_dataframe.head()")
    print(ts_dataframe.head())
    # get test data target
    test_data_target = ts_dataframe["target"].iloc[int(len(ts_dataframe) * train_test_data_split):]
    # add target to predictions
    predictions["target"] = test_data_target

    # Plot the predictions
    add_plot(predictions, "Predictions")
