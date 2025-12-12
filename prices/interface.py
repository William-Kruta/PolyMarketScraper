from .local import PricesDB
from .web import PricesScraper
from helper import get_data


def get_price_data(
    db_path: str, clob_token_id: str, date: str = "", force_update: bool = False
):

    db = PricesDB(db_path)
    scraper = PricesScraper()
    params = {"clob_token_id": clob_token_id, "date": date}
    data = get_data(
        read_func=db._read_price_data,
        read_params=params,
        fetch_func=scraper.fetch_prices,
        fetch_params=params,
        insert_func=db._insert_price_data,
        force_update=force_update,
    )
    return data
