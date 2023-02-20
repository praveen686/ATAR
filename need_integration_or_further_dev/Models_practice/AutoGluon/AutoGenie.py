# Import RAPIDS libraries for GPU-accelerated machine learning and data science workflows in Python 3.9 (https://rapids.ai/)
# GPU DataFrame library for loading, joining, aggregating, filtering and otherwise manipulating tabular data using a familiar Pandas-like API (https://docs.rapids.ai/api/cudf/stable/)
import cudf

# Import AutoGluon library for automatic machine learning in Python 3 (https://autogluon.mxnet.io/)
# AutoGluon allows users to easily apply deep learning to tabular datasets with little or no code changes required from the user
from autogluon import TabularPrediction as task

# Import SHAP library for interpretable machine learning in Python 3 (http://shap.readthedocs.io/en/latest/#)
# SHAP connects game theory with local explanations by uniting several previous methods and representing the result as a unified framework called SHAP values
import shap

# Import XGBoost library for gradient boosting decision trees in Python 3 (https://xgboost.readthedocs.io/en/latest/)
# XGBoost is an optimized distributed gradient boosting library designed to be highly efficient, flexible and portable
import xgboost as xgb

class AutoGenie:
    """
    AutoGenie is a framework for automatic machine learning using the RAPIDS, AutoGluon, SHAP, and XGBoost libraries in Python 3.9
    Natural Language Processing (NLP) is used to interpret and explain inputs, processes, and outputs to the end user in
    a way that is easy to understand as well as to provide a basis for further research and development.
    Documentation is provided in the form of docstrings for easy automatic documentation
    Because this is an accelerated framework, most components (even all) use GPU acceleration and tend to avoid copying of data and use of libraries like pandas and numpy
    Where inputs are not provided they are first infered from the data (types, shape, etc ...) automatically, meaning the end user can simply pass the url/obj for the data and the rest can be taken care of automatically

    e.g.
        # Import AutoGenie
        from autogenie import AutoGenie

        # Create an instance of the class
        ag = AutoGenie()

        ag.parse_data(url="https://raw.githubusercontent.com/automl/AutoGluon/master/tutorials/tabular_prediction/"
                       "data_files//FlightDelaysDataset-small.csv")  # Parse the data into a GPU DataFrame

        ag.train(label="DEP_DELAY", problem="regression", time=30, hyperparameters={'max_depth': 3})  # Train a model on the parsed data using AutoGluon with default settings and 30 seconds of training time

        ag.explain()  # Explain predictions to the end user in natural language using SHAP values

    TimeSeries forcast e.g.
        # Import AutoGenie
        from autogenie import AutoGenie

        # Create an instance of the class
        ag = AutoGenie()

        ag.parse_data(url="https://raw.githubusercontent.com/automl/AutoGluon/master/tutorials/"  # Parse the data into a GPU DataFrame using a time series parser (parses date and time fields)
                       "tabular_prediction/"
                       "data_files//FlightDelaysDataset-small.csv", timeseries=True)

         ag.train(label="DEP_DELAY", problem="regression", hyperparameters={'max_depth': 3})  # Train a model on the parsed data using AutoGluon with default settings and 30 seconds of training time, including features for each hour in day, month, year etc ... as well as weekdays vs weekends to allow forcast based on past trends at that specific hour in history (easter sunday or christmas eve will have different delays than other days due to holidays)

         predictions = ag.predict()  # Predict future values based on past trends by passing no parameters to predict method which uses defaults or pass custom dates and times e..g {'date': '2020-12-24', 'time': '23:59:00'}

         ag.explain()  # Explain predictions to the end user in natural language using SHAP values
    """

    def __init__(self):
        self.data = None
        self.label = None
        self.problem = None
        self.time = None
        self.hyperparameters = None
        self.model = None
        self.timeseries = None
        self.parsed_data = None
        self.predictions = None

    def parse_data(self, url, timeseries=False):
        """
        Parses the data into a GPU dataframe, using a time series parser if timeseries is True
        """
        self.timeseries = timeseries
        if timeseries:
            # parse data as a time series
            self.parsed_data = rapid.TimeSeriesData(url)
        else:
            # parse data as a regular GPU dataframe
            self.parsed_data = rapid.GPUDataFrame(url)

    def train(self, label, problem, time=None, hyperparameters=None):
        """
        Trains a model on the parsed data using AutoGluon
        """
        self.label = label
        self.problem = problem
        self.time = time
        self.hyperparameters = hyperparameters

        if self.problem == 'regression':
            self.model = autogluon.regression.AutoML(max_runtime=self.time, hyperparameters=self.hyperparameters).fit(
                self.parsed_data, self.label)
        elif self.problem == 'classification':
            self.model = autogluon.classification.AutoML(max_runtime=self.time,
                                                         hyperparameters=self.hyperparameters).fit(self.parsed_data,
                                                                                                   self.label)

    def predict(self, data=None):
        """
        Predicts values based on the trained model
        """
        if data is None:
            self.predictions = self.model.predict(self.parsed_data)
        else:
            self.predictions = self.model.predict(data)
        return self.predictions

    def explain(self):
        """
        Explains predictions to the end user in natural language using SHAP values
        """
        explainer = shap.Explainer(self.model, self.parsed_data)
        return explainer.shap_values(self.predictions)



# Create an instance of the class
ag = AutoGenie()

# Parse the data into a GPU DataFrame
ag.parse_data(url="https://raw.githubusercontent.com/automl/AutoGluon/master/tutorials/tabular_prediction/"
                "data_files//FlightDelaysDataset-small.csv")

# Train a model on the parsed data using AutoGluon with default settings and 30 seconds of training time
ag.train(label="DEP_DELAY", problem="regression", time=30, hyperparameters={'max_depth': 3})

# Explain predictions to the end user in natural language using SHAP values
ag.explain()

# Predict future values based on past trends by passing no parameters to predict method which uses defaults or pass custom dates and times e..g {'date': '2020-12-24', 'time': '23:59:00'}
predictions = ag.predict()

# Explain predictions to the end user in natural language using SHAP values
ag.explain()

