from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, exc, UniqueConstraint
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, exc, inspect
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
class PostgreSQLDatabase:
    def __init__(self, connection_string):
        # Establish a connection to the Postgres database
        self.engine = create_engine(connection_string)
        self.metadata = MetaData()

    def create_table(self):
        inspector = inspect(self.engine)
        if 'financial_data' not in inspector.get_table_names():
            metadata = MetaData()

            # Define a new table with a unique constraint on timestamp and symbol
            financial_data = Table('financial_data', metadata,
                Column('timestamp', DateTime, primary_key=True),
                Column('symbol', String),
                Column('open', Float),
                Column('high', Float),
                Column('low', Float),
                Column('close', Float),
                Column('volume', Float),
                UniqueConstraint('timestamp', 'symbol', name='uix_1')
            )
            metadata.create_all(self.engine)
            print("Table created")
        else:
            print("Table already exists")
    def upsert_data(self, data):
        # Upsert data into the table
        financial_data = Table('financial_data', self.metadata, autoload_with=self.engine)

        insert_stmt = insert(financial_data).values(data)
        do_update_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['timestamp', 'symbol'],
            set_=dict(open=insert_stmt.excluded.open, high=insert_stmt.excluded.high, low=insert_stmt.excluded.low, close=insert_stmt.excluded.close, volume=insert_stmt.excluded.volume)
        )

        with self.engine.connect() as connection:
            connection.execute(do_update_stmt)
        print("Data upserted")

    def query_data(self, symbol):
        # Query data from the table
        financial_data = Table('financial_data', self.metadata, autoload_with=self.engine)
        select_stmt = text(f"SELECT * FROM financial_data WHERE symbol = :symbol")
        with self.engine.connect() as connection:
            result = connection.execute(select_stmt, symbol=symbol)
            for row in result:
                print(row)

    def drop(self, table_name):
        # Drop a table
        inspector = inspect(self.engine)
        if inspector.has_table(table_name):
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            table.drop(self.engine)
            print(f"Table '{table_name}' dropped")
        else:
            print(f"No table named '{table_name}' found")
