import ast
import json
import datetime as dt
import polars as pl
import pickle
import numpy as np
from typing import Literal

from .local import EventsDB
from .web import EventsScraper
from helper import get_data


def get_events_data(
    db_path: str,
    event_id: str = "",
    event_name: str = "",
    scrape_func=None,
    active: bool = True,
    sort_by: Literal["dtr", "volume"] = "dtr",
    end_date_filter: Literal["event_end", "contract_end"] = "contract_end",
    use_for_dtr: Literal["event_end", "contract_end"] = "contract_end",
    force_update: bool = False,
    dtr: int = 10_000,
):
    """
    Get market data.

    Parameters
    ----------
    db_path : str
        Path to database.
    event_id : str, optional
        ID of the event, by default "", if blank fetch all.
    name : str, optional
        Name of the event, by default ""
    title : str, optional
        Title of the event, by default ""
    scrape_func : _type_, optional
        Function used to scrape, by default None, if None, will fallback to default.
    active: bool,
        Determines if only 'active' contracts are returned.
    sort_by: str,
        Determines how to sort the dataframe.
    end_date_filter: str
        Determines which columns to drop unknown values for.
    use_for_dtr: str
        Determines which date column to use for 'days-to-resolution' (dtr)
    force_update : bool, optional
        Determines if new data will be scraped and update database, by default False
    dtr: int
        Determines to include contracts with a dtr value lower than the parameter value.
        Example, if dtr = 3, contracts with 3 days or less to resolution will be returned.
    Returns
    -------
    pl.DataFrame
        Dataframe containing event data.
    """
    db = EventsDB(db_path)
    scraper = EventsScraper()

    if event_id != "" or event_name != "":
        scrape_func = scraper.fetch_event_by_X

    if scrape_func is None:
        scrape_func = scraper.fetch_top_active_markets
    params = {"event_id": event_id, "event_name": event_name}

    data = get_data(
        read_func=db._read_event_data,
        read_params=params,
        fetch_func=scrape_func,
        fetch_params=params,
        insert_func=[db._insert_event_data, db._insert_markets_data],
        force_update=force_update,
    )

    data = calc_dtr(data, use_for_dtr)

    data = data.filter(
        (pl.col("dtr") >= 0)
        & (pl.col("dtr") <= dtr)
        & (pl.col(end_date_filter) != "unk")
        & (pl.col("active") == active)
    ).sort(by=sort_by)
    return data


def get_markets_data(
    db_path: str,
    event_id: str = "",
    market_id: str = "",
    market_name: str = "",
    scrape_func=None,
    sort_by: Literal["dtr", "volume"] = "dtr",
    end_date_filter: Literal["event_end", "contract_end"] = "contract_end",
    use_for_dtr: Literal["event_end", "contract_end"] = "contract_end",
    force_update: bool = False,
    dtr: int = 10_000,
) -> pl.DataFrame:
    """
    Get market data.

    Parameters
    ----------
    db_path : str
        Path to database.
    event_id : str, optional
        ID of the event, by default "", if blank fetch all.
    market_id : str, optional
        ID of the market, by default "", if blank fetch all.
    name : str, optional
        Name of the event, by default ""
    title : str, optional
        Title of the event, by default ""
    scrape_func : _type_, optional
        Function used to scrape, by default None, if None, will fallback to default.
    sort_by: str,
        Determines how to sort the dataframe.
    end_date_filter: str
        Determines which columns to drop unknown values for.
    use_for_dtr: str
        Determines which date column to use for 'days-to-resolution' (dtr)
    force_update : bool, optional
        Determines if new data will be scraped and update database, by default False
    dtr: int
        Determines to include contracts with a dtr value lower than the parameter value.
        Example, if dtr = 3, contracts with 3 days or less to resolution will be returned.
    Returns
    -------
    pl.DataFrame
        Dataframe containing market data.
    """
    db = EventsDB(db_path)
    scraper = EventsScraper()
    if event_id != "" or market_name != "":
        scrape_func = scraper.fetch_event_by_X
    if scrape_func is None:
        scrape_func = scraper.fetch_top_active_markets
    params = {
        "event_id": event_id,
        "market_id": market_id,
        "market_name": market_name,
        "event_name": market_name,
    }
    df = get_data(
        read_func=db._read_market_data,
        read_params=params,
        fetch_func=scrape_func,
        fetch_params=params,
        insert_func=[db._insert_event_data, db._insert_markets_data],
        force_update=force_update,
    )
    df = calc_dtr(df, use_for_dtr)
    df = df.filter(
        (pl.col("dtr") >= 0)
        & (pl.col("dtr") <= dtr)
        & (pl.col(end_date_filter) != "unk")
    ).sort(by=sort_by)
    df = safe_parse_embedded_lists(df, "outcomes")
    df = safe_parse_embedded_lists(df, "clob_token_ids")
    return df


def get_X_where_Y(db_path: str, x_col: str, y_col: str, y_match_value, table_name: str):
    """
    Query the 'x_col' where 'y_col' = 'y_match_value'.

    Ex:
    x_col = "name"
    y_col = "id"
    y_match_value = "570360"

    This will return the contract name where the "id" = "570360".

    Parameters
    ----------
    db_path : str
        Path to database
    x_col : str
        Field to return.
    y_col : str
        Field to search.
    y_match_value
        Value to match.
    Returns
    -------
    The matched value, "None" if value not found.
    """
    db = EventsDB(db_path)
    query = f"SELECT {x_col} FROM {table_name} WHERE {y_col} = '{y_match_value}'"
    with db.conn:
        cursor = db.conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        return data


#####################################
# Update Status
#####################################


def update_expired_markets(db_path: str):
    """
    Checks all active markets and closes them if the end_date has passed.

    db_path: str
        Path to the database.
    """
    db = EventsDB(db_path)
    cursor = db.conn.cursor()

    # 1. Fetch only markets that are currently marked as active
    cursor.execute(f"SELECT id, end_date FROM {db.TABLE} WHERE active = 1")
    active_markets = cursor.fetchall()
    expired_ids = []
    now = dt.datetime.now(dt.timezone.utc)
    # 2. Iterate and check dates
    for market_id, end_date_str in active_markets:
        if not end_date_str:
            continue  # Skip if empty
        try:
            # Parse the stored date safely
            market_end_date = dt.datetime.fromisoformat(
                end_date_str.replace("Z", "+00:00")
            )
            # 3. Compare with current time
            if now > market_end_date:
                expired_ids.append(market_id)
                print(f"Marking market {market_id} as closed (Expired: {end_date_str})")
        except ValueError as e:
            print(f"Error parsing date for {market_id}: {e}")
    # 4. Batch Update
    if expired_ids:
        # Create a placeholder string like (?, ?, ?)
        placeholders = ", ".join(["?"] * len(expired_ids))

        query = f"""
            UPDATE {db.TABLE} 
            SET active = 0, closed = 1 
            WHERE id IN ({placeholders})
        """

        cursor.execute(query, expired_ids)
        db.conn.commit()
        print(f"Updated {len(expired_ids)} markets.")
    else:
        print("No markets needed updating.")

    db.conn.close()


def update_research_status(db_path: str, event_id: str, research_value: bool):
    """
    Update the 'research' field for an event oriented on "event_id".

    db_path: str
        Path to the database.
    event_id: str
        ID of the event to update.
    research_value: bool
        Value to update the 'researched' field with. If True, the event has been researched.
    """
    query = """UPDATE {} SET researched = ? WHERE id = ?"""
    params = (research_value, event_id)
    _update_status(db_path, query, params, "events")


def update_active_status(db_path: str, event_id: str, active_value: bool):
    """
    Update the 'active' field for an event oriented on "event_id".

    db_path: str
        Path to the database.
    event_id: str
        ID of the event to update.
    research_value: bool
        Value to update the 'active' field with. If True, the event is still active.
    """
    query = """UPDATE {} SET active = ? WHERE id = ?"""
    params = (active_value, event_id)
    _update_status(db_path, query, params, "events")


def update_closed_status(db_path: str, event_id: str, closed_value: bool):
    """
    Update the 'closed' field for an event oriented on "event_id".

    db_path: str
        Path to the database.
    event_id: str
        ID of the event to update.
    research_value: bool
        Value to update the 'closed' field with. If True, the event is closed.

    """
    query = """UPDATE {} SET closed = ? WHERE id = ?"""
    params = (closed_value, event_id)
    _update_status(db_path, query, params, "events")


def _update_status(db_path: str, query: str, params: tuple, table_name: str):
    db = EventsDB(db_path)
    with db.conn:
        cursor = db.conn.cursor()
        cursor.execute(
            query.format(table_name),
            params,
        )


def calc_dtr(df: pl.DataFrame, date_col: str):
    # Drop rows with unknown end_date
    # Parse the date string into a datetime object.
    df = df.filter((pl.col(date_col) != "unk")).with_columns(
        parsed_end_date=pl.col(date_col).str.to_datetime(time_zone="UTC")
    )
    # Calculate the 'days-to-resolve'(dtr) for the contract.
    # Days to resolve refers to when the contract ends and resolved the outcome.
    df = df.with_columns(
        dtr=(
            pl.col("parsed_end_date") - dt.datetime.now(dt.timezone.utc)
        ).dt.total_days()
    ).drop("parsed_end_date")
    return df


def safe_parse_embedded_lists(df: pl.DataFrame, column: str) -> pl.DataFrame:
    df = df.with_columns(
        pl.col(column)
        .str.replace_all(r"\\", "")  # Remove backslashes
        .str.strip_chars('"')  # Remove outer quotes first
        .str.strip_chars("[]")  # Then remove brackets
        .str.split(", ")  # Split by comma-space
        .map_elements(
            lambda x: [s.strip('"') for s in x], return_dtype=pl.List(pl.String)
        )
        .alias(column)  # Strip quotes from each element
    )
    return df
