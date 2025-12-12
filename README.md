# PolyMarketScraper

Collect event and market data for markets.

### Contracts

The `Contracts` class can get data about a contract.

###### Events

Below is an example of how to get event data with the `contract` class object.
**NOTE**: dtr = 'days to resolution', meaning how many days until the contract expires.

```
contract = Contract(event_name="fed-decision-in-january") # Create contract object for the event.
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

---

### General Use

###### Events

Events can be accessed through the `interface`.

```

from events.interface import get_event_data

data = get_events_data(db_path) # Get all event data.
data = get_events_data(db_path, event_id) # Get specific event.

============================

# You can also pass a specific scraper function when retrieving new events. For example...

from events.web import fetch_top_active_markets, fetch_soon_resolving_markets

data = get_events_data(db_path, scraper_func=fetch_top_active_markets) # Get specific event.


============================

┌───────┬─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┬───┬────────┬────────┬────────────┬──────┐
│ id    ┆ name                            ┆ title                           ┆ description                     ┆ … ┆ active ┆ closed ┆ researched ┆ dtr  │
│ ---   ┆ ---                             ┆ ---                             ┆ ---                             ┆   ┆ ---    ┆ ---    ┆ ---        ┆ ---  │
│ str   ┆ str                             ┆ str                             ┆ str                             ┆   ┆ i64    ┆ i64    ┆ i64        ┆ i64  │
╞═══════╪═════════════════════════════════╪═════════════════════════════════╪═════════════════════════════════╪═══╪════════╪════════╪════════════╪══════╡
│ 95453 ┆ elon-musk-of-tweets-december-5… ┆ Elon Musk # tweets December 5 … ┆ This market will resolve accor… ┆ … ┆ 1      ┆ 0      ┆ 0          ┆ 0    │
│ 92431 ┆ nfl-atl-tb-2025-12-11           ┆ Falcons vs. Buccaneers          ┆ In the upcoming NFL game, sche… ┆ … ┆ 1      ┆ 0      ┆ 0          ┆ 0    │
│ 97987 ┆ nba-por-nop-2025-12-11          ┆ Trail Blazers vs. Pelicans      ┆ In the upcoming NBA game, sche… ┆ … ┆ 1      ┆ 0      ┆ 0          ┆ 0    │
│ 81468 ┆ nhl-car-wsh-2025-12-12          ┆ Hurricanes vs. Capitals         ┆ In the upcoming NHL game, sche… ┆ … ┆ 1      ┆ 0      ┆ 0          ┆ 0    │
│ 97951 ┆ nba-lac-hou-2025-12-11          ┆ Clippers vs. Rockets            ┆ In the upcoming NBA game, sche… ┆ … ┆ 1      ┆ 0      ┆ 0          ┆ 0    │
│ …     ┆ …                               ┆ …                               ┆ …                               ┆ … ┆ …      ┆ …      ┆ …          ┆ …    │
│ 34050 ┆ russia-x-ukraine-ceasefire-bef… ┆ Russia x Ukraine ceasefire by … ┆ This market will resolve to "Y… ┆ … ┆ 1      ┆ 0      ┆ 0          ┆ 383  │
│ 30828 ┆ xi-jinping-out-before-2027      ┆ Xi Jinping out before 2027?     ┆ This market will resolve to "Y… ┆ … ┆ 1      ┆ 0      ┆ 0          ┆ 383  │
│ 30829 ┆ democratic-presidential-nomine… ┆ Democratic Presidential Nomine… ┆ This market will resolve to “Y… ┆ … ┆ 1      ┆ 0      ┆ 0          ┆ 1060 │
│ 31552 ┆ presidential-election-winner-2… ┆ Presidential Election Winner 2… ┆ The 2028 US Presidential Elect… ┆ … ┆ 1      ┆ 0      ┆ 0          ┆ 1060 │
│ 31875 ┆ republican-presidential-nomine… ┆ Republican Presidential Nomine… ┆ This market will resolve to “Y… ┆ … ┆ 1      ┆ 0      ┆ 0          ┆ 1060 │
└───────┴─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┴───┴────────┴────────┴────────────┴──────┘

```

###### Markets

Markets can be accessed through the `interface`.

```

from events.interface import get_market_id

data = get_market_id(db_path) # Get all market data.
data = get_market_id(db_path, market_id) # Get specific market.

┌──────────┬───────────┬─────────────────────────────────┬─────────────────────────────────┬───┬─────────────────────────────┬─────────────────────┬──────────────────────┬──────┐
│ event_id ┆ market_id ┆ name                            ┆ title                           ┆ … ┆ updated                     ┆ event_end           ┆ contract_end         ┆ dtr  │
│ ---      ┆ ---       ┆ ---                             ┆ ---                             ┆   ┆ ---                         ┆ ---                 ┆ ---                  ┆ ---  │
│ str      ┆ str       ┆ str                             ┆ str                             ┆   ┆ str                         ┆ str                 ┆ str                  ┆ i64  │
╞══════════╪═══════════╪═════════════════════════════════╪═════════════════════════════════╪═══╪═════════════════════════════╪═════════════════════╪══════════════════════╪══════╡
│ 95453    ┆ 793561    ┆ elon-musk-of-tweets-december-5… ┆ Will Elon Musk post 0-19 tweet… ┆ … ┆ 2025-12-06T16:33:52.098144Z ┆ 2025-12-12 00:00:00 ┆ 2025-12-12T17:00:00Z ┆ 0    │
│ 95453    ┆ 793562    ┆ elon-musk-of-tweets-december-5… ┆ Will Elon Musk post 20-39 twee… ┆ … ┆ 2025-12-06T16:33:55.467436Z ┆ 2025-12-12 00:00:00 ┆ 2025-12-12T17:00:00Z ┆ 0    │
│ 95453    ┆ 793563    ┆ elon-musk-of-tweets-december-5… ┆ Will Elon Musk post 40-59 twee… ┆ … ┆ 2025-12-07T16:31:43.081505Z ┆ 2025-12-12 00:00:00 ┆ 2025-12-12T17:00:00Z ┆ 0    │
│ 95453    ┆ 793564    ┆ elon-musk-of-tweets-december-5… ┆ Will Elon Musk post 60-79 twee… ┆ … ┆ 2025-12-07T16:31:40.823352Z ┆ 2025-12-12 00:00:00 ┆ 2025-12-12T17:00:00Z ┆ 0    │
│ 95453    ┆ 793565    ┆ elon-musk-of-tweets-december-5… ┆ Will Elon Musk post 80-99 twee… ┆ … ┆ 2025-12-07T16:31:42.966929Z ┆ 2025-12-12 00:00:00 ┆ 2025-12-12T17:00:00Z ┆ 0    │
│ …        ┆ …         ┆ …                               ┆ …                               ┆ … ┆ …                           ┆ …                   ┆ …                    ┆ …    │
│ 31875    ┆ 562089    ┆ will-person-cp-win-the-2028-re… ┆ Will Person CP win the 2028 Re… ┆ … ┆ 2025-07-11T19:44:01.640681Z ┆ null                ┆ 2028-11-07T00:00:00Z ┆ 1060 │
│ 31875    ┆ 562088    ┆ will-person-co-win-the-2028-re… ┆ Will Person CO win the 2028 Re… ┆ … ┆ 2025-07-11T19:44:01.38187Z  ┆ null                ┆ 2028-11-07T00:00:00Z ┆ 1060 │
│ 31875    ┆ 562017    ┆ will-person-v-win-the-2028-rep… ┆ Will Person V win the 2028 Rep… ┆ … ┆ 2025-07-11T19:42:49.276418Z ┆ null                ┆ 2028-11-07T00:00:00Z ┆ 1060 │
│ 31875    ┆ 562030    ┆ will-person-ai-win-the-2028-re… ┆ Will Person AI win the 2028 Re… ┆ … ┆ 2025-07-11T19:43:03.340509Z ┆ null                ┆ 2028-11-07T00:00:00Z ┆ 1060 │
│ 31875    ┆ 562094    ┆ will-person-cu-win-the-2028-re… ┆ Will Person CU win the 2028 Re… ┆ … ┆ 2025-07-11T19:44:06.497936Z ┆ null                ┆ 2028-11-07T00:00:00Z ┆ 1060 │
└──────────┴───────────┴─────────────────────────────────┴─────────────────────────────────┴───┴─────────────────────────────┴─────────────────────┴──────────────────────┴──────┘


```
