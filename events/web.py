import json
import requests
import datetime as dt

import polars as pl
from utils.dates import date_extract


class EventsScraper:
    def __init__(self):
        self.event_url = "https://gamma-api.polymarket.com/events"

    def fetch_soon_resolving_markets(
        self, resolve_threshold: int = 3, limit: int = 100
    ):
        """
        Fetches active Polymarket events and filters for those ending within 'days_soon'.
        """

        # Query parameters: active markets only, sorted by volume to get relevant ones
        params = {
            "closed": "false",
            "active": "true",
            "limit": limit,  # Fetch top 50 active events to scan
            "order": "volume",  # Sort by volume to see popular markets first
        }
        event_data, market_data = self._fetch_data(
            self.event_url, params, resolve_threshold=resolve_threshold
        )
        return event_data, market_data

    def fetch_top_active_markets(self, limit: int = 100):
        # API Parameters
        params = {
            "closed": "false",  # Only active markets
            "active": "true",  # Double check for active status
            "limit": limit,  # Number of events to fetch
            "order": "volume",  # Sort by volume
            "ascending": "false",  # Highest volume first
        }
        event_data, market_data = self._fetch_data(self.event_url, params)
        return event_data, market_data

    def fetch_event_by_X(self, event_id: str, event_name: str):
        # url = f"https://gamma-api.polymarket.com/events/{event_id}"
        if event_id != "":
            params = {"id": event_id}
        elif event_name != "":
            params = {"slug": event_name}
        event_data, market_data = self._fetch_data(self.event_url, params)
        return event_data, market_data

    def _fetch_data(self, url: str, params: dict = {}, resolve_threshold: int = 3000):
        event_data = {
            "id": [],
            "name": [],
            "title": [],
            "description": [],
            "volume": [],
            "created": [],
            "updated": [],
            "event_end": [],
            "contract_end": [],
            "active": [],
            "closed": [],
            "researched": [],
        }
        market_data = {
            "event_id": [],
            "id": [],
            "name": [],
            "title": [],
            "condition_id": [],
            "description": [],
            "outcomes": [],
            "volume": [],
            "clob_token_ids": [],
            "created": [],
            "updated": [],
            "event_end": [],
            "contract_end": [],
        }
        try:
            if params:
                response = requests.get(url, params=params)
            else:
                response = requests.get(url)
            response.raise_for_status()
            events = response.json()
            # Calculate the threshold date (current time + days_soon)
            now = dt.datetime.now(dt.timezone.utc)
            threshold_date = now + dt.timedelta(days=resolve_threshold)

            print(
                f"--- Markets Resolving by {threshold_date.strftime('%Y-%m-%d')} ---\n"
            )
            found_markets = False

            for event in events:
                end_date_str = event.get("endDate")
                event_id = event.get("id", "unk")
                event_name = event.get("ticker", "unk")
                description = event.get("description", "unk")
                if description == "unk":
                    event_end = "unk"
                else:
                    event_end = self._smart_extract(description, event_name)
                event_data["id"].append(event_id)
                event_data["name"].append(event_name)
                event_data["title"].append(event.get("title", "unk"))
                event_data["description"].append(description),
                event_data["volume"].append(event.get("volume", 0.0))
                event_data["created"].append(event.get("createdAt", "unk"))
                event_data["updated"].append(event.get("updatedAt", "unk"))
                event_data["event_end"].append(event_end)
                event_data["contract_end"].append(end_date_str)
                event_data["active"].append(event.get("active", True))
                event_data["closed"].append(event.get("closed", True))
                event_data["researched"].append(False)
                # Safely get the end date (usually in ISO format like '2024-12-31T23:59:00Z')

                if not end_date_str:
                    continue

                # Parse the ISO date string to a datetime object
                # Note: Python 3.11+ handles 'Z' automatically, for older versions replace 'Z'
                try:
                    event_end_date = dt.datetime.fromisoformat(
                        end_date_str.replace("Z", "+00:00")
                    )
                except ValueError:
                    continue

                # Check if the event ends between NOW and our THRESHOLD
                if now < event_end_date <= threshold_date:
                    found_markets = True
                    markets = event.get("markets", [])
                    if markets:
                        for m in markets:
                            outcomes = m.get("outcomes", [])
                            prices = m.get("outcomePrices")
                            market_name = m.get("slug", "unk")
                            market_description = m.get("description", "unk")
                            if market_description == "unk":
                                market_end = "unk"
                            else:
                                market_end = self._smart_extract(
                                    market_description, market_name
                                )

                            if isinstance(outcomes, str):
                                outcomes = json.dumps(outcomes)
                            if isinstance(prices, str):
                                prices = json.loads(prices)
                            market_data["event_id"].append(event_id)
                            market_data["id"].append(m.get("id", "unk"))
                            market_data["name"].append(market_name)
                            market_data["title"].append(m.get("question", "unk"))
                            market_data["condition_id"].append(
                                m.get("conditionId", "unk")
                            )
                            market_data["description"].append(market_description)
                            market_data["outcomes"].append(outcomes)
                            market_data["volume"].append(m.get("volumeNum", 0))
                            market_data["clob_token_ids"].append(
                                m.get("clobTokenIds", "unk")
                            )
                            market_data["created"].append(m.get("createdAt", "unk"))
                            market_data["updated"].append(m.get("updatedAt", "unk"))
                            market_data["event_end"].append(market_end)
                            market_data["contract_end"].append(m.get("endDate", "unk"))

            if not found_markets:
                print("No high-volume markets found resolving in this window.")

            event_data = pl.DataFrame(event_data)
            market_data = pl.DataFrame(market_data)
            return event_data, market_data

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")

    def _smart_extract(self, description: str, name: str):
        end = date_extract(description)
        if end is None:
            end = date_extract(name)
            if end is None:
                end = "unk"
            else:
                end = dt.datetime.strftime(end, "%Y-%m-%d %H:%M:%S")
        else:
            end = dt.datetime.strftime(end, "%Y-%m-%d %H:%M:%S")
        return end
