import requests
import datetime as dt

import polars as pl


def fetch_tag_id(tag_name: str = ""):
    """
    Fetches all tags and finds the ID for the given name (case-insensitive).
    """
    url = "https://gamma-api.polymarket.com/tags"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tags = response.json()
        tag_data = []
        # Look for a match
        tag_name_lower = tag_name.lower()
        for tag in tags:
            # The API returns 'label' (display name) and 'id'
            if tag.get("label", "").lower() == tag_name_lower and tag_name != "":
                return tag.get("id")
            elif tag.get("slug", "").lower() == tag_name_lower:
                return tag.get("id")
            else:
                tag_data.append({"name": tag.get("label").lower(), "id": tag.get("id")})
        # No 'tag_name' is passed,
        if tag_name == "":
            return pl.DataFrame(tag_data)
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tags: {e}")
        return None
