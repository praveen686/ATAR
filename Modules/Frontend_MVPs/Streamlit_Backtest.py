import streamlit as st
# print current directory

from Modules.Backtests.Backtest_Interface import Backtest_Interface




# Initialize interface
if 'bt_interface' not in st.session_state:
    st.session_state.bt_interface = None

catalog_path = st.text_input("Enter catalog path",
                             "/home/ruben/PycharmProjects/Genie-Trader/Data/catalog")  # todo inputs
if st.session_state.bt_interface is None:
    st.session_state.bt_interface = Backtest_Interface(catalog_path)

# Set time period
start_time = st.text_input("Enter start time", "2021-01-05")
end_time = st.text_input("Enter end time", "2022-01-06")
st.session_state.bt_interface.set_time_period(start_time, end_time)

# Select instruments
instr_index = st.number_input("Enter instrument index to add", min_value=0, value=0, step=1)
st.session_state.bt_interface.add_instrument(instr_index)

# Show selected instruments
st.write("Selected Instruments: ", st.session_state.bt_interface.instruments)

# Configure data
if st.button("Configure data"):
    st.session_state.bt_interface.add_data_config()
    st.write("Data configured successfully")

# Configure venues
if st.button("Configure venue"):
    st.session_state.bt_interface.add_venue_config()
    st.write("Venue configured successfully")

# Configure strategy
strategy_path = st.text_input("Enter strategy path", "nautilus_trader.examples.strategies.ema_cross:EMACross")
config_path = st.text_input("Enter config path", "nautilus_trader.examples.strategies.ema_cross:EMACrossConfig")
fast_ema_period = st.number_input("Enter fast EMA period", min_value=0, value=10, step=1)
slow_ema_period = st.number_input("Enter slow EMA period", min_value=0, value=20, step=1)
trade_size = st.number_input("Enter trade size", min_value=0, value=1000000, step=1)

if st.button("Configure strategy"):
    st.session_state.bt_interface.add_strategy_config(strategy_path, config_path, fast_ema_period, slow_ema_period,
                                                      trade_size)
    st.write("Strategy configured successfully")

# Run configuration and node
if st.button("Run backtest"):
    st.session_state.bt_interface.run_config()
    result = st.session_state.bt_interface.run_node()
    st.write("Backtest run successfully. Result: ", result)
