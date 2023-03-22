import pickle

import numpy as np
import pandas as pd


def triple_barrier_meta_labeling_X_y(triple_barrier_labeled_data, feature_columns, return_as_df=False):
    """
    Most have ["open", "low", "high", "close", "volume", "bin", "label_side"] columns
    :param triple_barrier_labeled_data:
    :return:
    """

    if not return_as_df:
        X = triple_barrier_labeled_data[["open", "low", "high", "close", "volume"]].values
        bins = np.squeeze(triple_barrier_labeled_data[['bin']].values)
        y = np.squeeze(triple_barrier_labeled_data[['label_side']].values) * bins
    else:
        bins = np.squeeze(triple_barrier_labeled_data[['bin']].values)
        triple_barrier_labeled_data["target"] = np.squeeze(triple_barrier_labeled_data[['label_side']].values) * bins

        return triple_barrier_labeled_data[feature_columns], triple_barrier_labeled_data["target"]

    return X, y


def train_model(  # todo generalize this to work with any model and any data set/type
        triple_barrier_labeled_data,
        train_test_data_split=0.8,
        prediction_length=1,
        time_limit=60 * 60 * 24 * 7,
        static_features=None,
        timestamp_column="Datetime",
        id_column="id",
        num_gpu=0,
        feature_columns=None,

):
    """
    Need ["open", "low", "high", "close", "volume", "bin", "label_side"] columns


    :param triple_barrier_labeled_data:
    :return:
    """
    from imblearn.over_sampling import SMOTE
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

    if feature_columns is None:
        feature_columns = ["open", "low", "high", "close", "volume"]

    X, y = triple_barrier_meta_labeling_X_y(triple_barrier_labeled_data,
                                            feature_columns=feature_columns,
                                            return_as_df=True)

    from need_integration_aka_scattered_work.Models_practice.AutoGluon.autogluon_help import prepare_autogluon_data
    ts_dataframe = prepare_autogluon_data(X_df=X, y_df=y,
                                          prediction_length=prediction_length,
                                          id_column=id_column,
                                          timestamp_column=timestamp_column,
                                          static_features=static_features,
                                          )

    # Split data into train and test
    from need_integration_aka_scattered_work.Models_practice.AutoGluon.autogluon_help import split_data
    # todo splitdata can use the autogluon splitter or sklearn splitter instead of this simple one below
    train_data, test_data = split_data(ts_dataframe=ts_dataframe, train_test_data_split=train_test_data_split)

    # First Model
    from need_integration_aka_scattered_work.Models_practice.AutoGluon.autogluon_help import get_timeseries_predictor
    primary_predictor = get_timeseries_predictor(load_model=False, prediction_length=prediction_length)
    primary_predictor.fit(train_data, presets="medium_quality", time_limit=time_limit, num_gpus=num_gpu, )
    primary_predictor.save()
    predictor_summary = primary_predictor.fit_summary()
    predictor_leaderboard = primary_predictor.leaderboard()
    print("Primary Model")
    print(predictor_summary)
    print(predictor_leaderboard)

    print("test_data.head()")
    print(test_data.head())

    primary_y_pred = primary_predictor.predict(test_data, num_gpu=1,  # known_covariates=future_known_covariates
                                               )
    print("primary_y_pred.head()")
    print(primary_y_pred["mean"])
    exit()
    # # fixme delete or replace
    # X_train, y_train = X[:train_length], y[:train_length]
    # X_test, y_test = X[train_length:], y[train_length:]
    # # bins_train, bins_test = bins[:train_length], bins[train_length:]
    #
    # sm = SMOTE()  # todo add this as an optional action to take
    # X_train_res, y_train_res = sm.fit_resample(X_train, y_train)  # todo add this as an optional action to take
    #
    # # fixme delete or replace
    # # First Model
    # primary_model = LogisticRegression().fit(X_train_res, y_train_res)
    # primary_y_pred = primary_model.predict(X_test)  # Predicted labels for test data to be used in meta labeling

    # Confusion Matrix
    tbl = true_binary_label(primary_y_pred.values, test_data["target"].values)
    cm = confusion_matrix(tbl, primary_y_pred != 0)
    print(cm)
    cm_display = ConfusionMatrixDisplay(cm).plot()
    cm_display.figure_.savefig("confusion_matrix.png")

    # Prep for meta labeling training
    # generate predictions for training set
    y_train_pred = primary_predictor.predict(
        # all train_data columns except target
        train_data.drop(columns=["target"]),
    )
    # add the predictions to features
    X_train_meta = np.hstack([y_train_pred[:, None], train_data.drop(columns=["target"])])
    X_test_meta = np.hstack([primary_y_pred[:, None], test_data.drop(columns=["target"])])

    # Meta Model Training
    # generate true meta-labels
    y_train_meta = true_binary_label(y_train_pred, train_data["target"])
    # rebalance classes again
    sm = SMOTE()
    X_train_meta_res, y_train_meta_res = sm.fit_resample(X_train_meta, y_train_meta)
    meta_model = LogisticRegression().fit(X_train_meta_res, y_train_meta_res)
    #
    # Meta Model Testing
    y_pred_meta = meta_model.predict(X_test_meta)
    # use meta-predictions to filter primary predictions
    cm = confusion_matrix(true_binary_label(primary_y_pred, test_data["target"]), (primary_y_pred * y_pred_meta) != 0)
    print(cm)
    cm_display = ConfusionMatrixDisplay(cm).plot()
    cm_display.figure_.savefig("meta_confusion_matrix.png")
    return primary_predictor, meta_model


def live_execution_of_models(open, low, high, close, volume, primary_model=None, meta_model=None):
    if primary_model is None or meta_model is None:
        raise ValueError("Models are not provided.")

    X = np.array([open, low, high, close, volume]).reshape(1, -1)
    y_pred = primary_model.predict(X)
    X_meta = np.hstack([y_pred[:, None], X])
    y_pred_meta = meta_model.predict(X_meta)
    y_prob_meta = meta_model.predict_proba(X_meta)

    # Predicted Values
    pred_result = y_pred * y_pred_meta
    pred_result = pred_result[0]

    # Probability Values
    prob_result = y_pred * y_prob_meta
    prob_result = prob_result[0]

    # Combine the results
    result = [pred_result, prob_result]
    return result


def true_binary_label(y_pred, y_test):
    bin_label = np.zeros_like(y_pred)
    for i in range(y_pred.shape[0]):
        if y_pred[i] != 0 and y_pred[i] * y_test[i] > 0:
            bin_label[i] = 1  # true positive
    return bin_label


def save_primary_n_meta_model_pickles(primary_model_path, meta_model_path):
    with open(primary_model_path, 'wb') as f:
        pickle.dump(primary_model_path, f)
    with open(meta_model_path, 'wb') as f:
        pickle.dump(meta_model_path, f)


def load_primary_n_meta_model_pickles(primary_model_path, meta_model_path):
    # Load the model
    with open(primary_model_path, 'rb') as f:
        primary_model = pickle.load(f)
    with open(meta_model_path, 'rb') as f:
        meta_model = pickle.load(f)
    return primary_model, meta_model
