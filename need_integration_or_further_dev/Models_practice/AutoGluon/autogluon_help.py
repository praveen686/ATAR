import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor


def prepare_autogluon_data(
        X_df, y_df,
        id_column, # e.g.
        timestamp_column="Datetime",
        static_features=None,  # e.g. [{"id": "XAUUSD", "type": "commodity", "currency": "USD"}]
        prediction_length=1,
   ):  # todo generalize this function
    # add id column and target column



    raw_data_frame = X_df.copy()
    raw_data_frame['id'] = id_column
    raw_data_frame['target'] = y_df

    # drop NaNs
    clean_data_frame = raw_data_frame.dropna()


    # create TimeSeriesDataFrame
    ts_dataframe = TimeSeriesDataFrame.from_data_frame(
        clean_data_frame,
        id_column="id",
        timestamp_column=timestamp_column,
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
):
    if load_model:
        predictor = TimeSeriesPredictor.load("model")
    else:
        predictor = TimeSeriesPredictor(
            prediction_length=prediction_length,
            eval_metric="MASE",
            # known_covariates_names=["weekend"],
            freq="1 min",
            ignore_time_index=True,
            num_gpus=1,

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
