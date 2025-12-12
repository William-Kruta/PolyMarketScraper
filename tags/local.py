import polars as pl
from database import Database


class TagsDB(Database):
    def __init__(self, db_path: str, log: bool = True):
        self.TABLE = "tags"
        super().__init__(db_path, log)
        self._create_tags_table()

    def _create_tags_table(self):
        query = f"""CREATE TABLE IF NOT EXISTS {self.TABLE} (
                    name TEXT NOT NULL,
                    id TEXT NOT NULL,
                    PRIMARY KEY (id));
                    """
        index = f"CREATE INDEX IF NOT EXISTS idx_tags_ti_ts ON {self.TABLE} (name, id);"
        self._init_schema(query, index)

    def _insert_tags_data(self, df: pl.DataFrame):
        query = f"""INSERT OR IGNORE INTO {self.TABLE} (name, id)
                    VALUES (?, ?);
                """
        self._insert_data(df, query)

    def _read_tags_data(self, tag_id: str, tag_name: str = ""):
        query = f"""SELECT * FROM {self.TABLE}"""

        if tag_id is not None and tag_id != "":
            query += " WHERE id = ?"
            params = (tag_id,)
        elif tag_name is not None and tag_name != "":
            query += " WHERE name = ?"
            params = (tag_name,)
        else:
            params = ()
        print(f"QUERY: {query}")
        data = self._read_data(query, params)
        return data
