# PolyMarketScraper

Collect event and market data for markets.

### Contracts

The `Contracts` class can get data about a contract.

###### Events

Below is an example of how to get event data with the `contract` class object.
**NOTE**: dtr = 'days to resolution', meaning how many days until the contract expires.

```
contract = Contract(event_name="fed-decision-in-january")
# Get the possible outcomes
data = contract.get_event_data()

### Result

┌───────┬─────────────────────────┬──────────────────────────┬─────────────────────────────────┬───┬────────┬────────┬────────────┬─────┐
│ id    ┆ name                    ┆ title                    ┆ description                     ┆ … ┆ active ┆ closed ┆ researched ┆ dtr │
│ ---   ┆ ---                     ┆ ---                      ┆ ---                             ┆   ┆ ---    ┆ ---    ┆ ---        ┆ --- │
│ str   ┆ str                     ┆ str                      ┆ str                             ┆   ┆ i64    ┆ i64    ┆ i64        ┆ i64 │
╞═══════╪═════════════════════════╪══════════════════════════╪═════════════════════════════════╪═══╪════════╪════════╪════════════╪═════╡
│ 45883 ┆ fed-decision-in-january ┆ Fed decision in January? ┆ The FED interest rates are def… ┆ … ┆ 1      ┆ 0      ┆ 0          ┆ 46  │
└───────┴─────────────────────────┴──────────────────────────┴─────────────────────────────────┴───┴────────┴────────┴────────────┴─────┘


```

###### Market

Below is an example of how to get market data with the `contract` class object.

```
contract = Contract(event_name="fed-decision-in-january")
# Get the possible outcomes
data = contract.get_market_data()

### Result

┌──────────┬───────────┬─────────────────────────────────┬─────────────────────────────────┬───┬─────────────────────────────┬───────────┬──────────────────────┬─────┐
│ event_id ┆ market_id ┆ name                            ┆ title                           ┆ … ┆ updated                     ┆ event_end ┆ contract_end         ┆ dtr │
│ ---      ┆ ---       ┆ ---                             ┆ ---                             ┆   ┆ ---                         ┆ ---       ┆ ---                  ┆ --- │
│ str      ┆ str       ┆ str                             ┆ str                             ┆   ┆ str                         ┆ null      ┆ str                  ┆ i64 │
╞══════════╪═══════════╪═════════════════════════════════╪═════════════════════════════════╪═══╪═════════════════════════════╪═══════════╪══════════════════════╪═════╡
│ 45883    ┆ 601697    ┆ fed-decreases-interest-rates-b… ┆ Fed decreases interest rates b… ┆ … ┆ 2025-12-12T01:53:24.082795Z ┆ null      ┆ 2026-01-28T00:00:00Z ┆ 46  │
│ 45883    ┆ 601698    ┆ fed-decreases-interest-rates-b… ┆ Fed decreases interest rates b… ┆ … ┆ 2025-12-12T01:53:45.150108Z ┆ null      ┆ 2026-01-28T00:00:00Z ┆ 46  │
│ 45883    ┆ 601699    ┆ no-change-in-fed-interest-rate… ┆ No change in Fed interest rate… ┆ … ┆ 2025-12-12T01:50:58.336672Z ┆ null      ┆ 2026-01-28T00:00:00Z ┆ 46  │
│ 45883    ┆ 601700    ┆ fed-increases-interest-rates-b… ┆ Fed increases interest rates b… ┆ … ┆ 2025-12-12T01:46:40.082682Z ┆ null      ┆ 2026-01-28T00:00:00Z ┆ 46  │
└──────────┴───────────┴─────────────────────────────────┴─────────────────────────────────┴───┴─────────────────────────────┴───────────┴──────────────────────┴─────┘

```

###### Outcomes

```
contract = Contract(event_name="fed-decision-in-january")
# Get the possible outcomes
data = contract.get_outcomes(verbose=True)
┌──────────┬───────────┬───────────────┐
│ event_id ┆ market_id ┆ outcomes      │
│ ---      ┆ ---       ┆ ---           │
│ str      ┆ str       ┆ list[str]     │
╞══════════╪═══════════╪═══════════════╡
│ 95453    ┆ 793561    ┆ ["Yes", "No"] │
│ 95453    ┆ 793562    ┆ ["Yes", "No"] │
│ 95453    ┆ 793563    ┆ ["Yes", "No"] │
│ 95453    ┆ 793564    ┆ ["Yes", "No"] │
│ 95453    ┆ 793565    ┆ ["Yes", "No"] │
│ …        ┆ …         ┆ …             │
│ 31552    ┆ 561328    ┆ ["Yes", "No"] │
│ 31552    ┆ 561349    ┆ ["Yes", "No"] │
│ 31552    ┆ 561262    ┆ ["Yes", "No"] │
│ 31552    ┆ 561315    ┆ ["Yes", "No"] │
│ 31552    ┆ 561337    ┆ ["Yes", "No"] │
└──────────┴───────────┴───────────────┘
```

### General Use

### Events

Events can be accessed through the `interface`.

```

from events.interface import get_event_data

data = get_events_data(db_path) # Get all event data.
data = get_events_data(db_path, event_id) # Get specific event.

============================

# You can also pass a specific scraper function when retrieving new events. For example...

from events.web import fetch_top_active_markets, fetch_soon_resolving_markets

data = get_events_data(db_path, scraper_func=fetch_top_active_markets) # Get specific event.

```

### Markets

Markets can be accessed through the `interface`.

```

from events.interface import get_market_id

data = get_market_id(db_path) # Get all market data.
data = get_market_id(db_path, market_id) # Get specific market.

```

```

```
