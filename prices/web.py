import requests
import polars as pl
import pandas as pd


class PricesScraper:
    def __init__(self):
        pass

    def fetch_prices(self, clob_token_id: str, interval: str = "1d"):
        url = "https://clob.polymarket.com/prices-history"

        params = {
            "market": int(clob_token_id),  # CRITICAL: This must be the Token/Asset ID
            "interval": interval,
            "fidelity": 60,  # Resolution in minutes (optional)
        }
        print(f"CLOB: {clob_token_id}")
        try:
            response = requests.get(url, params=params)
            print(f"RESPONSE: {response}")
            response.raise_for_status()
            data = response.json()

            if not data.get("history"):
                print("No history found. Check your Token ID.")
                return None

            # Convert to DataFrame for easier reading
            df = pd.DataFrame(data["history"])

            # Convert unix timestamp to readable date
            df["date"] = pd.to_datetime(df["t"], unit="s")
            df = df.rename(columns={"p": "price"})
            df["clob_token_id"] = clob_token_id
            df = pl.from_pandas(df)
            df = df.with_columns(pl.col("date").dt.to_string("%Y-%m-%d %H:%M:%S"))
            return df.select(["clob_token_id", "date", "price"])

        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
