import pandas as pd
import streamlit as st
from nautilus_trader.core.datetime import dt_to_unix_nanos, unix_nanos_to_dt
from nautilus_trader.persistence.catalog import ParquetDataCatalog
import swifter
import vectorbtpro as vbt # noqa F401

# clear cache to avoid memory leak or slow down
st.cache(allow_output_mutation=True)


def load_catalog(catalog_path):
    return ParquetDataCatalog(catalog_path)

catalog_path = "../../Data/catalog"
catalog = load_catalog(catalog_path)


def load_instruments(catalog):
    return catalog.instruments()


instruments = load_instruments(catalog)


# Analytics Page
def page_query_data():
    st.title('Query Data')

    # selected_instrument = st.selectbox('Select an instrument', catalog.instruments().id.to_list())

    selected_instruments = st.multiselect('Select instruments', catalog.instruments().id.to_list())


    start_date = st.date_input('Start date', value=pd.to_datetime('2021-01-04'))
    end_date = st.date_input('End date', value=pd.to_datetime('2021-01-05'))

    if st.button('Analyze Data'):
        start = dt_to_unix_nanos(pd.Timestamp(start_date, tz="UTC"))
        end = dt_to_unix_nanos(pd.Timestamp(end_date, tz="UTC"))
        for selected_instrument in selected_instruments:
            ticks = catalog.quote_ticks(start=start, end=end, instrument_ids=[selected_instrument])
            # Perform some basic analysis
            ticks['bid'] = ticks['bid'].astype(float)
            ticks['ask'] = ticks['ask'].astype(float)

            bid_ask_spread = ticks['ask'] - ticks['bid']
            st.write(f'Average bid-ask spread: {bid_ask_spread.mean()}')
            selected_instrument_info = catalog.instruments(instrument_ids=[selected_instrument])
            st.json(selected_instrument_info.to_dict(orient='records'))

            # Display the raw data #execute_kwargs=dict(engine="threadpool")
            ticks.index = ticks["ts_event"].map(unix_nanos_to_dt) # faq: does this work in parallel? A: yes, map is parallel by default
            # ticks.index = ticks["ts_event"].swifter.apply(unix_nanos_to_dt)
            from time import perf_counter
            st.write("Plotting ...")
            start = perf_counter()
            plot = ticks[['bid', 'ask']].vbt.plot()
            st.write(f"Plotting 1 took {perf_counter() - start} seconds")
            start = perf_counter()
            st.plotly_chart(plot, use_container_width=False, width=1000, height=500)
            st.write(f"Plotting 2 took {perf_counter() - start} seconds")



# Set up the Streamlit app
st.sidebar.title('Catalog')
page = st.sidebar.radio('Go to', ['Query'])

if page == 'Query':
    page_query_data()

# todo config for different instrument values as well as being able to specify per asset if needed
# todo add a way to ingest data from a csv file
# todo
