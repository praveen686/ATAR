import os

# import vectorbtpro as vbt

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

input_csv_file = st.file_uploader("Upload CSV File", type="csv", accept_multiple_files=False, siz)

# Prepare data
if input_csv_file is not None:
    data = pd.read_csv(input_csv_file)
    genie_loader = Genie_Loader()
    data = genie_loader.from_pandas(data)
    print(f'{data  =}')

