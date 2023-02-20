import whisper

import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor
import cudf
import cupy
import torch


LOAD_MODEL = False
PREDICTION_LENGTH = 7
TRAINING_TIME_LIMIT = 240
TRAIN_TEST_DATA_SPLIT = 0.8

"""Data Preprocessing"""
raw_data_frame = pd.read_csv("XAUUSD.csv", index_col=None, parse_dates=["Datetime"])
# add id column
raw_data_frame['id'] = "XAUUSD"
# add target column (shifted by 1) and turn it into a classification problem (1 if price goes up, -1 if price goes
# down and 0 if price stays the same within threshold of 0.01)
# raw_data_frame['target'] = raw_data_frame['Close'].pct_change(PREDICTION_LENGTH).shift(-1)
raw_data_frame['target'] = raw_data_frame['Close'].pct_change(PREDICTION_LENGTH).shift(-1)
raw_data_frame['target'] = raw_data_frame['target'].apply(lambda x: 1 if x > 0.01 else -1 if x < -0.01 else 0)

# drop NaNs
raw_data_frame = raw_data_frame.dropna()
# add static features
raw_static_features = pd.DataFrame(
    data=[{"id": "XAUUSD", "type": "commodity", "currency": "USD"}],
).set_index("id")

ts_dataframe = TimeSeriesDataFrame.from_data_frame(
    raw_data_frame,
    id_column="id",
    timestamp_column="Datetime",
)
ts_dataframe.static_features = raw_static_features

# Split the data into train and test 80 and 20
train_data = ts_dataframe.iloc[:int(len(ts_dataframe) * TRAIN_TEST_DATA_SPLIT)]
test_data = ts_dataframe.iloc[int(len(ts_dataframe) * TRAIN_TEST_DATA_SPLIT):]

print("train_data")
print(train_data.head())
print("test_data")
print(test_data.head())


# from autogluon.timeseries.splitter import MultiWindowSplitter
#
# splitter = MultiWindowSplitter(num_windows=5)
# _, test_data_multi_window = splitter.split(test_data, PREDICTION_LENGTH)


if LOAD_MODEL:
    predictor = TimeSeriesPredictor.load("model")
else:
    predictor = TimeSeriesPredictor(
        prediction_length=PREDICTION_LENGTH,
        eval_metric="MASE",
        # known_covariates_names=["weekend"],
        freq="1 min",
        ignore_time_index=True,
        num_gpus=1,

    )
    predictor.fit(train_data, presets="medium_quality", time_limit=TRAINING_TIME_LIMIT,
                  num_gpus=1,

                  )

print(predictor.fit_summary())
predictor.save()
# print("predictor.leaderboard()")
# print(predictor.leaderboard())

predictions = predictor.predict(
    test_data,
    # known_covariates=future_known_covariates
    num_gpu=1,
)
print(predictions.head())


# Plot the predictions
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
test_data_target = raw_data_frame["target"].iloc[int(len(ts_dataframe) * TRAIN_TEST_DATA_SPLIT):]
# add target to predictions
predictions["target"] = test_data_target

add_plot(predictions, "Predictions")
