import pickle

import numpy as np


def train_model(  # todo generalize this to work with any model and any data set
        triple_barrier_labeled_data,
):
    """
    Need ["open", "low", "high", "close", "volume", "bin", "label_side"] columns


    :param triple_barrier_labeled_data:
    :return:
    """
    from imblearn.over_sampling import SMOTE
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

    original_length = len(triple_barrier_labeled_data)
    train_length = int(original_length * 0.8)  # todo add this as a parameter

    X = triple_barrier_labeled_data[["open", "low", "high", "close", "volume"]].values
    bins = np.squeeze(triple_barrier_labeled_data[['bin']].values)
    y = np.squeeze(triple_barrier_labeled_data[['label_side']].values) * bins

    X_train, y_train = X[:train_length], y[:train_length]
    X_test, y_test = X[train_length:], y[train_length:]
    # bins_train, bins_test = bins[:train_length], bins[train_length:]

    sm = SMOTE()  # todo add this as an optional action to take
    X_train_res, y_train_res = sm.fit_resample(X_train, y_train)  # todo add this as an optional action to take

    # First Model
    primary_model = LogisticRegression().fit(X_train_res, y_train_res)
    y_pred = primary_model.predict(X_test)  # Predicted labels for test data to be used in meta labeling
    cm = confusion_matrix(true_binary_label(y_pred, y_test), y_pred != 0)
    print(cm)
    cm_display = ConfusionMatrixDisplay(cm).plot()
    cm_display.figure_.savefig("confusion_matrix.png")


    # Prep for meta labeling training
    # generate predictions for training set
    y_train_pred = primary_model.predict(X_train)
    # add the predictions to features
    X_train_meta = np.hstack([y_train_pred[:, None], X_train])
    X_test_meta = np.hstack([y_pred[:, None], X_test])

    # Meta Model Training
    # generate true meta-labels
    y_train_meta = true_binary_label(y_train_pred, y_train)
    # rebalance classes again
    sm = SMOTE()
    X_train_meta_res, y_train_meta_res = sm.fit_resample(X_train_meta, y_train_meta)
    meta_model = LogisticRegression().fit(X_train_meta_res, y_train_meta_res)
    #
    # Meta Model Testing
    y_pred_meta = meta_model.predict(X_test_meta)
    # use meta-predictions to filter primary predictions
    cm = confusion_matrix(true_binary_label(y_pred, y_test), (y_pred * y_pred_meta) != 0)
    print(cm)
    cm_display = ConfusionMatrixDisplay(cm).plot()
    cm_display.figure_.savefig("meta_confusion_matrix.png")
    return primary_model, meta_model


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

