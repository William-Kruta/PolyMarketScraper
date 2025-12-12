import ast
import pickle
import polars as pl
from .local import EventsDB
from .interface import get_events_data, get_markets_data, get_X_where_Y

try:
    from ..prices.interface import get_price_data
except ImportError:
    from prices.interface import get_price_data


class Contract:
    def __init__(self, event_id: str, event_name: str, db_path: str):
        self.db_path = db_path
        if event_id == "":
            self.event_id = self._get_event_id_by_slug(event_name)
            self.event_name = event_name
        if event_name == "":
            self.event_id = event_id
            self.event_name = self._get_event_slug_by_id(event_id)

        self.db = EventsDB(db_path)

    def __str__(self):
        data = self.get_event_data()
        event_end = data["event_end"][0]
        end = data["contract_end"][0]
        desc = data["description"][0]
        return f"""
        ID: {self.event_id}
        Name: {self.event_name}
        EVENT END: {event_end}
        CONTRACT END: {end}    
        
        Description: {desc}

        """

    def get_market_ids(self, id_col: str = "market_id") -> list:
        data = get_markets_data(self.db_path, event_id=self.event_id)
        return data[id_col]

    def get_event_data(self, force_update: bool = False):
        if self.event_id == "":
            params = {
                "db_path": self.db_path,
                "event_name": self.event_name,
                "force_update": force_update,
            }
        else:
            params = {
                "db_path": self.db_path,
                "event_id": self.event_id,
                "force_update": force_update,
            }
        data = get_events_data(**params)
        return data

    def get_market_data(self, market_id: str = "", force_update: bool = False):
        params = {
            "db_path": self.db_path,
            "event_id": self.event_id,
            "force_update": force_update,
        }
        if market_id != "":
            params["market_id"] = market_id

        data = get_markets_data(**params)
        return data

    def get_clob_token_ids(
        self, market_id: str = "", verbose: bool = False, force_update: bool = False
    ) -> list:
        data = get_markets_data(
            self.db_path,
            event_id=self.event_id,
            market_id=market_id,
            force_update=force_update,
        )
        if market_id != "":
            data = data.filter(pl.col("market_id") == market_id)
        if verbose:
            df = data.select(["event_id", "market_id", "clob_token_ids"])
            return df
        else:
            return data["clob_token_ids"]

    def get_outcomes(self, market_id: str = "", verbose: bool = False) -> list:
        data = get_markets_data(self.db_path, market_id=market_id)
        if market_id != "":
            data = data.filter(pl.col("market_id") == market_id)
        if verbose:
            df = data.select(["event_id", "market_id", "outcomes"])
            return df
        else:
            return data["outcomes"]

    def get_prices(
        self, market_id: str = "", clob_token_id: str = "", force_update: bool = False
    ) -> pl.DataFrame:
        if clob_token_id == "":
            token_map = self._create_token_mapping(market_id)
        else:
            token_map = self._create_token_mapping(market_id, clob_token_id)
        data = []
        for k, v in token_map.items():
            df = get_price_data(self.db_path, k, force_update=force_update)
            df = df.with_columns(outcome=pl.lit(v))
            data.append(df)
        price_df = pl.concat(data)
        return price_df

    def download_all(self):
        self.get_market_data()
        self.get_event_data()
        self.get_prices()

    def _create_token_mapping(self, market_id: str = "", clob_token_id: str = ""):
        if clob_token_id == "":
            if market_id == "":
                market_id = self.get_market_ids()
            else:
                if isinstance(market_id, str):
                    market_id = [market_id]
            token_map = {}
            for mid in market_id:
                clob_ids = self.get_clob_token_ids(mid)
                outcomes = self.get_outcomes(mid)
                for c_list, o_list in zip(clob_ids, outcomes):
                    # Update dict in bulk instead of looping item-by-item
                    token_map.update(zip(c_list, o_list))
        else:
            clob_ids = list(self.get_clob_token_ids(market_id)[0])
            outcomes = list(self.get_outcomes(market_id)[0])
            token_map = {}
            token_map[clob_token_id] = self._get_corresponding_outcome(
                clob_token_id, clob_ids, outcomes
            )
        return token_map

    def _build_params(self):
        if self.event_id == "":
            params = {"db_path": self.db_path, "event_name": self.event_name}
        else:
            params = {"db_path": self.db_path, "event_id": self.event_id}
        return params

    def _get_corresponding_outcome(self, target, search_list, result_list):
        try:
            # index() stops at the first match, making it O(N)
            idx = search_list.index(target)
            return result_list[idx]
        except ValueError:
            return None  # Target not found in search_list
        except IndexError:
            return None

    def _get_event_id_by_slug(self, slug: str):
        event_id = get_X_where_Y(self.db_path, "id", "name", slug, table_name="events")
        try:
            return event_id[0][0]
        except IndexError:
            return None

    def _get_event_slug_by_id(self, event_id: str) -> str:
        slug = get_X_where_Y(self.db_path, "name", "id", event_id, "events")
        try:
            return slug[0][0]
        except IndexError:
            return None
