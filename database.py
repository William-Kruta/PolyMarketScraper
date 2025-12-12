import sqlite3
from pathlib import Path
from typing import Self

import polars as pl


class Database:
    def __init__(self, db_path: str, log: bool = True):
        self.db_path = Path(db_path)
        self.log = log
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = self._connect()

    def _connect(self, timeout: int = 30) -> sqlite3.Connection:
        conn = sqlite3.connect(
            str(self.db_path), timeout=timeout, detect_types=sqlite3.PARSE_DECLTYPES
        )
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 30000;")
        return conn

    def _init_schema(self, create_table_query: str, index_query: str) -> None:
        cur = self.conn.cursor()
        cur.execute(create_table_query)
        if index_query != "":
            cur.execute(index_query)
        cur.close()

    def close(self) -> None:
        try:
            self.conn.commit()
        except Exception:
            pass
        self.conn.close()

    # context manager support
    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def _read_data(
        self,
        read_query: str,
        params: tuple = None,
    ):

        with self.conn:
            cur = self.conn.cursor()
            if params is None:
                cur.execute(read_query)
            else:
                cur.execute(read_query, params)
            rows = cur.fetchall()
            columns = [col[0] for col in cur.description]
            if not rows:
                df = pl.DataFrame({c: [] for c in columns})
            else:
                df = pl.from_records(
                    rows, schema=columns, orient="row", infer_schema_length=None
                )

            return df

    def _insert_data(self, df: pl.DataFrame, insert_query: str) -> None:
        if df.is_empty():
            return

        if self.log:
            print(f"Inserting/updating {len(df)} records into the database...")
        records = df.to_numpy().tolist()
        with self.conn:
            self.conn.executemany(insert_query, records)

    def _drop_table(self, table_name: str):
        with self.conn:
            cursor = self.conn.cursor()
            query = f"DROP TABLE {table_name}"
            cursor.execute(query)

    def _build_param_query(self, base_query: str, column_map: dict, **kwargs):
        conditions = []
        params = []
        for arg, value in kwargs.items():
            # Check if the argument is valid and the value is not empty
            if arg in column_map and value not in (None, ""):
                db_col = column_map[arg]

                # Build the condition string (e.g., "id = ?")
                conditions.append(f"{db_col} = ?")
                params.append(value)

        # 3. Assemble the query
        if conditions:
            # " AND " joins multiple conditions (e.g., "id = ? AND title = ?")
            base_query += " WHERE " + " AND ".join(conditions)

        return base_query, tuple(params)
