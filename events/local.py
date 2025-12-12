import polars as pl
from database import Database

from sqlite3 import OperationalError


class EventsDB(Database):
    def __init__(self, db_path: str, log: bool = True):
        self.TABLE = "events"
        self.MARKET_TABLE = "markets"
        super().__init__(db_path, log)
        self._create_events_table()
        self._create_markets_table()

    def _create_events_table(self):
        query = f"""CREATE TABLE IF NOT EXISTS {self.TABLE} (
                    id TEXT NOT NULL,
                    name TEXT,
                    title TEXT,
                    description TEXT,
                    volume REAL,
                    created TEXT,
                    updated TEXT,
                    event_end TEXT,
                    contract_end TEXT,
                    active BOOLEAN,
                    closed BOOLEAN,
                    researched BOOLEAN,
                    PRIMARY KEY (id));
                    """
        self._init_schema(query, "")

    def _create_markets_table(self):
        query = f"""CREATE TABLE IF NOT EXISTS {self.MARKET_TABLE} (
                    event_id TEXT NOT NULL,
                    market_id TEXT NOT NULL,
                    name TEXT,
                    title TEXT,
                    condition_id TEXT,
                    description TEXT,
                    outcomes TEXT,
                    volume REAL,
                    clob_token_ids TEXT,
                    created TEXT,
                    updated TEXT,
                    event_end TEXT,
                    contract_end TEXT,
                    PRIMARY KEY (event_id, market_id));
                    """
        self._init_schema(query, "")

    def _insert_event_data(self, df: pl.DataFrame):
        query = f"""INSERT OR IGNORE INTO {self.TABLE} (id, name, title, description, volume, created, updated, event_end, contract_end, active, closed, researched)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """
        self._insert_data(df, query)

    def _insert_markets_data(self, df: pl.DataFrame):
        query = f"""INSERT OR IGNORE INTO {self.MARKET_TABLE} (event_id, market_id, name, title, condition_id, description, outcomes, volume, clob_token_ids, created, updated, event_end, contract_end)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """
        self._insert_data(df, query)

    def _read_event_data(self, event_id: str, event_name: str = ""):
        query = f"""SELECT * FROM {self.TABLE}"""
        column_map = {"event_id": "id", "event_name": "name"}
        final_query, params = self._build_param_query(
            query,
            column_map,
            event_id=event_id,
            event_name=event_name,
        )
        try:
            data = self._read_data(final_query, params)
        except OperationalError:
            self._create_events_table()
            data = self._read_data(final_query, params)
        return data

    def _read_market_data(
        self,
        event_id: str,
        market_id: str = "",
        market_name: str = "",
    ):
        query = f"""SELECT * FROM {self.MARKET_TABLE}"""
        column_map = {
            "event_id": "event_id",
            "market_id": "market_id",
            "market_name": "name",
        }
        final_query, params = self._build_param_query(
            query,
            column_map,
            event_id=event_id,
            market_id=market_id,
            market_name=market_name,
        )
        try:
            data = self._read_data(final_query, params)
        except OperationalError:
            self._create_markets_table()
            data = self._read_data(final_query, params)
        return data
