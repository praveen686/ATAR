import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor


def preprocess_data(data_frame, prediction_length):  # todo generalize this function
    # add id column
    data_frame['id'] = "XAUUSD"
    # add target column (shifted by 1) and turn it into a classification problem (1 if price goes up, -1 if price goes
    # down and 0 if price stays the same within threshold of 0.01)
    data_frame['target'] = data_frame['Close'].pct_change(prediction_length).shift(-1)
    data_frame['target'] = data_frame['target'].apply(lambda x: 1 if x > 0.01 else -1 if x < -0.01 else 0)

    # drop NaNs
    data_frame = data_frame.dropna()
    # add static features
    raw_static_features = pd.DataFrame(
        data=[{"id": "XAUUSD", "type": "commodity", "currency": "USD"}],
    ).set_index("id")

    ts_dataframe = TimeSeriesDataFrame.from_data_frame(
        data_frame,
        id_column="id",
        timestamp_column="Datetime",
    )
    ts_dataframe.static_features = raw_static_features
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

    # get test data target
    test_data_target = raw_data_frame["target"].iloc[int(len(ts_dataframe) * train_test_data_split):]
    # add target to predictions
    predictions["target"] = test_data_target

    # Plot the predictions
    add_plot(predictions, "Predictions")
