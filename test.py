from tags.web import fetch_tag_id
from tags.interface import get_tag_id
from events.interface import (
    get_events_data,
    get_markets_data,
    update_research_status,
    update_expired_markets,
    get_X_where_Y,
)
from events.web import EventsScraper
from prices.web import PricesScraper
from events.contract import Contract

# scraper = EventsScraper()

# data = scraper.fetch_event_by_X("45883")
# print(data)

# event, market = scraper.fetch_top_active_markets()

# event_data, market_data = scraper.fetch_top_active_markets()

# print(market_data["prices"])
# exit()
DB_PATH = "events.db"
contract = Contract("", "fed-decision-in-january", DB_PATH)
# contract.download_all()

data = contract.get_market_data()

print(f"Data: {data}")
# clob = contract.get_clob_token_ids()

# data = event_scraper.fetch_top_active_markets()


# clob = contract.get_outcomes("540206")
# name = get_X_where_Y(
#     DB_PATH,
#     x_col="clob_token_ids",
#     y_col="market_id",
#     y_match_value="570360",
#     table_name="markets",
# )


# data = scraper2.fetch_prices(
#     "74018646712472971445258547247048869505144598783748525202442089895996249694683"
# )


exit()

# data = get_events_data(DB_PATH)
# data = fetch_soon_resolving_markets()

# data2 = get_markets_data(DB_PATH)
# update_expired_markets(DB_PATH)
# update_research_status(DB_PATH, "23656", False)


# data = get_markets_data(DB_PATH)
# data = get_tag_id(DB_PATH, "dating")
