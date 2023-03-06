import os


import vectorbtpro as vbt

import pandas as pd
import streamlit as st
import sys
sys.path.append('/home/ruben/PycharmProjects/Genie-Trader/need_integration_or_further_dev/Dev_Modules')
from genie_loader import Genie_Loader


"""
Triple Barrier Labeling for OHLCV Data Dashboard using Streamlit

    Will be serving endpoints rather than locally since different environments and 
    resources will be used for data collection and model training
"""

input_csv_file = st.file_uploader("Upload CSV File", type="csv", accept_multiple_files=False)

# Prepare data
if input_csv_file is not None:
    data = pd.read_csv(input_csv_file)
    print(f'{input_csv_file  =}')
    # st.dataframe(data)

    genie_loader = Genie_Loader()
    data = genie_loader.from_pandas(data)
    print(f'{data  =}')


    # symbols_data_obj = genie_loader.fetch_data(data_file_names=data_file_names, data_file_dirs=data_file_dirs,
    #                                            rename_columns={"Open": "open", "High": "high", "Low": "low",
    #                                                            "Close": "close", "Tick volume": "volume"})
    #
    # '''Label the sides of the entries when the decision is made, not when the trade is opened -1 0 1 labeled series'''
    # side_df = sample_arb_strategy(
    #     OHLCV_Data=symbols_data_obj,
    #     R_parameters={},
    #     # todo make sure to pass inputs as a dict/json of parameter values to the function
    #     **{}
    # )
    #
    # '''todo: This is a hotfix due to only working with one asset at the moment'''
    # close_series = symbols_data_obj.close  # needs to be only one asset otherwise dimensionality error in multiindex
    # side_series = side_df[side_df.keys()[0]]
    #
    # '''Using the close and side series and other tbl configuration parameters, label --> triple barrier labeling'''
    # triple_barrier_labeled_data = daily_vol_triple_barrier_label_example(close_series=close_series,
    #                                                                      side_series=side_series, **tbl_kwargs)
    #
    # '''Combine the OHLCV data triple barrier labeled data'''
    # # remember the close values are the same as the close values in the symbols_data_obj so we can drop one
    # input_ohlcv_df = symbols_data_obj.get()
    # triple_barrier_labeled_data = triple_barrier_labeled_data.drop(columns=["close"]).join(input_ohlcv_df)
    # triple_barrier_labeled_data.index.names = ["Datetime"]
    #
    # triple_barrier_labeled_data = triple_barrier_labeled_data[
    #     input_ohlcv_df.columns.tolist() + ["prim_target", "meta_target"]]
    # print(triple_barrier_labeled_data.head())
    #
    # '''Save the triple barrier labeled data to be used in other processes'''
    # triple_barrier_labeled_data.to_csv("triple_barrier_labeled_data.csv", )
    # triple_barrier_labeled_data.to_pickle("triple_barrier_labeled_data.pickle")


