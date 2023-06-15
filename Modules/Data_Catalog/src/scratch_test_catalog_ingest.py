import pandas as pd
from nautilus_trader.core.datetime import dt_to_unix_nanos
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.persistence.external.core import process_files, write_objects
from nautilus_trader.persistence.external.readers import CSVReader
from nautilus_trader.test_kit.providers import TestInstrumentProvider

from Modules.Catalog.src.data_to_catalog import custom_parser_csv
catalog_path = "/home/ruben/PycharmProjects/Genie-Trader/Data/catalog"  # todo change to dynamic and/or buckets
catalog = ParquetDataCatalog(catalog_path)
currencies = {
    "AUDUSD": {
        "file_path": "raw_data/Forex/Majors/AUDUSD_Tick_*.csv",
        "header": None,
        "datetime_format": "%Y.%m.%d %H:%M:%S.%f",
    },
    "EURUSD": {
        "file_path": "raw_data/Forex/Majors/EURUSD_Tick_*.csv",
        "header": None,
        "datetime_format": "%Y.%m.%d %H:%M:%S.%f",
    },
    "GBPUSD": {
        "file_path": "raw_data/Forex/Majors/GBPUSD_Tick_*.csv",
        "header": None,
        "datetime_format": "%Y.%m.%d %H:%M:%S.%f",
    },
    "NZDUSD": {
        "file_path": "raw_data/Forex/Majors/NZDUSD_Tick_*.csv",
        "header": None,
        "datetime_format": "%Y.%m.%d %H:%M:%S.%f",
    },
    "USDCAD": {
        "file_path": "raw_data/Forex/Majors/USDCAD_Tick_*.csv",
        "header": None,
        "datetime_format": "%Y.%m.%d %H:%M:%S.%f",
    },
    "USDCHF": {
        "file_path": "raw_data/Forex/Majors/USDCHF_Tick_*.csv",
        "header": None,
        "datetime_format": "%Y.%m.%d %H:%M:%S.%f",
    },
    "USDJPY": {
        "file_path": "raw_data/Forex/Majors/USDJPY_Tick_*.csv",
        "header": None,
        "datetime_format": "%Y.%m.%d %H:%M:%S.%f",
    }
}



for currency, data in currencies.items():
    instrument = TestInstrumentProvider.default_fx_ccy(currency)
#     # todo check if there maybe?
#     process_files(
#         glob_path=data["file_path"],
#         reader=CSVReader(
#             block_parser=lambda x: parser_csv(x, instrument_id=instrument.id, datetime_format=data["datetime_format"]),
#             header=data["header"],
#             chunked=False,
#             as_dataframe=False,
#         ),
#         catalog=catalog,
#         # block_size="10mb",
#     )
#
    write_objects(catalog, [instrument])

print(catalog.instruments())
start_date = pd.to_datetime("2021-01-04")
end_date = pd.to_datetime("2021-01-05")

ticks = catalog.quote_ticks(start=start_date, end=end_date,
                            # instrument_ids=[selected_instrument]
                            )
print(ticks)
