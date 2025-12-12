from database import Database

import polars as pl
from sqlite3 import OperationalError


class PricesDB(Database):
    def __init__(self, db_path: str, log: bool = True):
        self.TABLE = "prices"
        super().__init__(db_path, log)

    def _create_prices_table(self):
        query = f"""CREATE TABLE IF NOT EXISTS {self.TABLE} (
                    clob_token_id TEXT,
                    date TEXT,
                    price TEXT,
                    PRIMARY KEY (clob_token_id, date));
                    """
        self._init_schema(query, "")

    def _insert_price_data(self, df: pl.DataFrame):
        query = f"""INSERT OR IGNORE INTO {self.TABLE} (clob_token_id, date, price)
                    VALUES (?, ?, ?);
                """
        self._insert_data(df, query)

    def _read_price_data(
        self,
        clob_token_id: str = "",
        date: str = "",
    ):
        query = f"""SELECT * FROM {self.TABLE}"""
        column_map = {
            "clob_token_id": "clob_token_id",
            "date": "date",
        }
        final_query, params = self._build_param_query(
            query,
            column_map,
            clob_token_id=clob_token_id,
            date=date,
        )
        try:
            data = self._read_data(final_query, params)
        except OperationalError:
            self._create_prices_table()
            data = self._read_data(final_query, params)
        return data
