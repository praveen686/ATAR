# from autogluon.tabular import TabularDataset, TabularPredictor
# train_data = TabularDataset('https://autogluon.s3.amazonaws.com/datasets/Inc/train.csv')
# test_data = TabularDataset('https://autogluon.s3.amazonaws.com/datasets/Inc/test.csv')
# predictor = TabularPredictor(label='class').fit(train_data=train_data)
# predictions = predictor.predict(test_data)
# print(predictions)

import brainome as bo

# import example training and test data from brainome
train_data = bo.download_dataset_url('https://brainome-public.s3.amazonaws.com/data/iris_train.csv')


exit()
# # Start the H2O cluster (locally)
# h2o.init()
#
# # Import a sample binary outcome train/test set into H2O
# train = h2o.import_file("https://s3.amazonaws.com/erin-data/higgs/higgs_train_10k.csv")
# test = h2o.import_file("https://s3.amazonaws.com/erin-data/higgs/higgs_test_5k.csv")
#
# # Identify predictors and response
# x = train.columns
# y = "response"
# x.remove(y)
#
# # For binary classification, response should be a factor
# train[y] = train[y].asfactor()
# test[y] = test[y].asfactor()
#
#
# # Run AutoML for 20 base models
# aml = H2OAutoML(max_models=20, seed=1)
# aml.train(x=x, y=y, training_frame=train)
#
# # View the AutoML Leaderboard
# lb = aml.leaderboard
# lb.head(rows=lb.nrows)  # Print all rows instead of default (10 rows)
# # from h2oai_client import Client
# # address = 'http://ip_where_driverless_is_running:12345'
# # username = 'username'
# # password = 'password'
# # cli = Client(address=address, username=username, password=password)
#
# exit()