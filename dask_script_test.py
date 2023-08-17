




# from datetime import datetime, timedelta
#
# from Modules.PostgreSQLDatabase.PostgreSQLDatabase import PostgreSQLDatabase
# import pandas as pd
# import redis
# from dask.distributed import Client
#
# # connect to Dask
# client = Client('localhost:8786')
#
# db = PostgreSQLDatabase('postgresql://postgres:postgres@localhost:5432/testdb')
# db.drop('financial_data')
# db.create_table()
#
# data = [
#     {'timestamp': datetime.now(), 'symbol': 'AAPL', 'open': 145.1, 'high': 146.0, 'low': 144.5, 'close': 145.6,
#      'volume': 2000000.0},
#     {'timestamp': datetime.now() + timedelta(microseconds=1), 'symbol': 'AAPL', 'open': 145.6, 'high': 146.5,
#      'low': 145.0, 'close': 146.1, 'volume': 1800000.0},
#     {'timestamp': datetime.now() + timedelta(microseconds=2), 'symbol': 'AAPL', 'open': 146.1, 'high': 147.0,
#      'low': 145.5, 'close': 146.6, 'volume': 2100000.0}
# ]
#
# db.upsert_data(data)
#
# db.query_data('AAPL')
