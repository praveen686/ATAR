# Outputs from Genie __> [R parameters] * [Sim Metrics "Features"]
# Currently this module assumes that only one asset
# Wanted to have parameter sensitivity report and tbl trained model done here but will split and later on combine into
#   another pipeline which makes better use of resources and the flow of operations like backtests
#   Thus here the ag model is trained on what is believed to be the optimal parameter combinations (which are passed)
#   For now only one parameter combination and asset are used (will be expanded on) and will not optimize

"""Summary:
    ag = autogluon
::
"""
import numpy as np
import pandas as pd

from need_integration_or_further_dev.Labeling_Strategies.sample_arb_strategy import sample_arb_strategy
from need_integration_or_further_dev.Dev_Modules.Triple_Barrier_Label.Triple_Barrier_Label import \
    daily_vol_triple_barrier_label_example


# todo class or function ...
def full_triple_barrier_meta_labeling_pipeline(Strategy_Function, OHLCV_Data, R_parameters, MPortfolio_Features,
                                               strategy_kwargs=None, **tbl_kwargs):
    """
    Inputs:
        - ***

    Outputs:
        - Metrics
        - Plots
        - Tables
        - Endpoints
        - ***

    todo add control to steer the flow of which microservices are run when this function is called
    todo labeling of sides should be done with pf sim in mind
    """

    # Run AutoGluon on the optimal R parameters, generate the optimal ensemble model, and return model,
    #           metrics for Optimal Path Strategy Report and Model, [plots, tables]
    # todo currently only handles one asset but needs to handle multiple
    ag_model, report = ag_triple_barrier_meta_labeling(Strategy_Function=Strategy_Function, OHLCV_Data=OHLCV_Data,
                                                       R_parameters=R_parameters,
                                                       MPortfolio_Features=MPortfolio_Features,
                                                       strategy_kwargs=strategy_kwargs, **tbl_kwargs)

    # Creation of "Deployment" Content Assistant for easy deployment of the model [dashboard, endpoints, etc.]
    # e.g. compile, ....

    ...


def ag_triple_barrier_meta_labeling(Strategy_Function, OHLCV_Data, R_parameters, MPortfolio_Features,
                                    strategy_kwargs=None, **tbl_kwargs):
    """
    This function is used to generate the optimal ensemble model for the input R parameters' returns. It organizes and
    schedules the microservices needed to:
        - Collect and prepare the data of returns for all R parameters
        - Label the data using the triple barrier labeling method
        - Train the optimal ensemble model using AutoGluon
        - Evaluate the model's performance
        - Generate the metrics, plots, tables, and endpoints for the model's performance
        - Return [compiled] model for AWS deployment


    Inputs:
        - Strategy_Function = e.g. vbt.MMT_strategy with args provided or Strategy_Redis_Obj to pull inputs from Redis
        - R parameters = e.g. {"r1": 0.01, "r2": 0.02, "r3": 0.03} or {"r1": [0.01, 0.02, 0.03],
            "r2": [0.01, 0.02, 0.03], "r3": [0.01, 0.02, 0.03]}
            values to the function
        - MPortfolio Features = str or list of str e.g.
                                        ["close", "volume", "open", "high", "low", 101-alpha, other strategies ... ]
                                defaults to Genie default MPortfolio Features and labeling but also those separately as
                                    well as manual or automatic feature engineering/validation and importance ranking
                                    to be used during the hyperparameter optimization process
        - strategy_kwargs = e.g. {"num_cores": 1}
        - tbl_kwargs = e.g. {"pt_sl": [0.5, 1],"min_ret": 0.0005, "num_threads": 28,"vertical_barrier_num_days": 1}



    Outputs:
        - Metrics
        - Plots
        - Tables
        - Endpoints
    """

    # todo: add a check to make sure that the inputs are valid

    # Label using Strategy_Function # Expected output:  [TimeSeriesDataFrame of Labels] * [R parameters]
    side_df = Strategy_Function(  # todo [currently outputs -1 0 1 labeled series]
        OHLCV_Data=OHLCV_Data,
        R_parameters=R_parameters,  # todo make sure to pass inputs as a dict/json of parameter values to the function
        **strategy_kwargs
    )
    # todo: add a check to make sure that the outputs are valid

    # Label using Triple Barrier Labeling # Expected output:  [TimeSeriesDataFrame of Labels] * [R parameters] + [MPortfolio Features] + [Target] # todo needs to handle multiple assets
    # todo/fixme Since this function currently only handles one asset we will just use the first asset for now
    close_series = OHLCV_Data.close  # needs to be only one asset otherwise dimensionality error in multiindex
    side_series = side_df[side_df.keys()[0]]

    triple_barrier_labeled_data = daily_vol_triple_barrier_label_example(close_series=close_series,
                                                                         side_series=side_series, **tbl_kwargs)

    # Auto-Model Ensemble Optimization [Autogluon]
    # Call autogluon functions

    ag_model, report = None, None
    return ag_model, report


if __name__ == "__main__":

    RELOAD_DATA = False

    from need_integration_or_further_dev.old_modules.genie_loader import Genie_Loader

    data_file_names = ["XAUUSD.csv"]
    data_file_dirs = ["../../../Data"]
    pickle_file_name = "XAUUSD.pickle"
    genie_loader = Genie_Loader()
    if RELOAD_DATA:
        symbols_data = genie_loader.fetch_data(data_file_names=data_file_names, data_file_dirs=data_file_dirs,
                                               rename_columns={"Open": "open", "High": "high", "Low": "low",
                                                               "Close": "close", "Tick volume": "volume"})
        symbols_data.save(pickle_file_name)
    else:
        symbols_data = genie_loader.load_pickle(pickle_file_name)

    full_triple_barrier_meta_labeling_pipeline(
        Strategy_Function=sample_arb_strategy, OHLCV_Data=symbols_data,
        R_parameters={
            "fast_windows": [10, 20, 30],
            "slow_windows": [20, 30, 40]
        }, MPortfolio_Features=["defaults"], strategy_kwargs={
        },
        **{
            "test_n_elements": 10_000,
            "pt_sl": [0.5, 1],
            "min_ret": 0.0005,
            "num_threads": 28,
            #
            #  Number of D/H/m/s to add for vertical barrier
            "vertical_barrier_num_days": 1,
            "vertical_barrier_num_hours": 0,
            "vertical_barrier_num_minutes": 0,
            "vertical_barrier_num_seconds": 0,
            #
        })
