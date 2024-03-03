from matplotlib import pyplot as plt

if __name__ == "__main__":
    import pandas as pd

    # DATADIR = '/home/ruben/PycharmProjects/Genie-Trader/dev_studies_workdir/tbml_output'
    DATADIR = '/home/ruben/PycharmProjects/Genie-Trader/Data/raw_data/Forex/Majors/Minute'
    # DATADIR = '/home/ruben/PycharmProjects/Genie-Trader/Data/raw_data'

    DATA_FILE_NAMES = [
        # "XAUUSD_GMT+0_NO-DST_M1.csv",
        # "US_Brent_Crude_Oil_GMT+0_NO-DST_M1.csv",
        # 'AAPL_1min_sample.csv',
        # 'BTC_1min_sample.csv',
        # 'ES_1min_sample.csv',
        # 'MSFT_1min_sample.csv',
        # 'QQQ_1min_sample.csv',
        # 'SPY_1min_sample.csv'
        'XAUUSD_GMT+0_NO-DST_M1.csv',
    ]
    # DATA_FILE_NAMES = [
    #     'AAPL_1min_sample_tbml_data.csv',
    #     'BTC_1min_sample_tbml_data.csv',
    #     'ES_1min_sample_tbml_data.csv',
    #     'MSFT_1min_sample_tbml_data.csv',
    #     'QQQ_1min_sample_tbml_data.csv',
    #     'SPY_1min_sample_tbml_data.csv'
    # ]
    # DATETIME_COLUMN_NAMES = 'timestamp'
    # DATETIME_COLUMN_NAMES = 'datetime'
    DATETIME_COLUMN_NAMES = 'Datetime'

    dataset = []
    for data_file_name in DATA_FILE_NAMES:
        data = pd.read_csv(
            f'{DATADIR}/{data_file_name}')
        data['symbol'] = data_file_name
        dataset.append(data)
    data = pd.concat(dataset, axis=0)

    pd.options.display.max_columns = None
    print(data.columns)
    print(data.head(10))

    data = data.dropna()
    # Parse the datetime column if necessary
    data[DATETIME_COLUMN_NAMES] = pd.to_datetime(data[DATETIME_COLUMN_NAMES])

    # Assuming 'close' is your variable of interest and 'target' is what you're predicting
    len_of_data = data.shape[0]

    t_train = data[DATETIME_COLUMN_NAMES].values[:int(len_of_data * 0.7) - 10]
    t_test = data[DATETIME_COLUMN_NAMES].values[-int(len_of_data * 0.3) - 10:]

    _ = data.pop(DATETIME_COLUMN_NAMES)
    _ = data.pop('symbol')

    X_train = data.values[:int(len_of_data * 0.7) - 10]
    X_test = data.values[-int(len_of_data * 0.3) - 10:]

    # Import the SINDy model
    import pysindy as ps

    # Initialize a differentiation method
    differentiation_method = ps.FiniteDifference(order=3)

    # Initialize the feature library. For example, polynomial features of up to degree 3:
    feature_library = ps.PolynomialLibrary(degree=3)

    # Initialize the optimizer, e.g., STLSQ optimizer
    optimizer = ps.STLSQ(threshold=0.01)

    # Initialize and fit the SINDy model focusing on the 'close' column dynamics
    model = ps.SINDy(
        differentiation_method=differentiation_method,
        feature_library=feature_library,
        optimizer=optimizer,
        feature_names=data.columns
    )
    model.fit(X_train)

    model.print()

    print(model.predict(x=X_test))

    # Predict derivatives using the learned model
    x_dot_test_predicted = model.predict(X_test)

    # Compute derivatives with a finite difference method, for comparison
    x_dot_test_computed = model.differentiate(X_test,  # t=dt
                                              )

    fig, axs = plt.subplots(X_test.shape[1], 1, sharex=True, figsize=(12, 12))
    for i in range(X_test.shape[1]):
        axs[i].plot(t_test, x_dot_test_computed[:, i], "k", label="numerical derivative")
        axs[i].plot(t_test, x_dot_test_predicted[:, i], "r--", label="model prediction")
        axs[i].legend()
        axs[i].set(xlabel="t", ylabel=r"$\dot x_{}$".format(i))
    fig.show()
