import re
import calendar
from datetime import datetime
from dateutil import parser


def date_extract(text, default_year=None):
    """
    Extracts a deadline date from a slug, title, or description.
    Handles:
    1. ISO Format (2025-12-31)
    2. "Before [Year]" logic (before-2026 -> 2025-12-31)
    3. Slug Dates without Year (december-31 -> 2025-12-31)
    4. Natural Language (December 31st, 2025)
    """

    # Default to current year if not provided
    if default_year is None:
        default_year = datetime.now().year

    # --- CASE 1: ISO Date Format (YYYY-MM-DD) ---
    # Matches: "2025-12-11", "2026-01-01"
    iso_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if iso_match:
        return datetime(
            int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
        )

    # --- CASE 2: "Before [Year]" Logic ---
    # Matches: "before-2026", "before 2026" -> Returns Dec 31, [Year-1]
    before_match = re.search(r"before-?(\d{4})", text, re.IGNORECASE)
    if before_match:
        return datetime(int(before_match.group(1)) - 1, 12, 31)

    # --- CASE 3: Slug Date (Month-Day) WITHOUT Year ---
    # Matches: "december-31", "january-15", "march-01"
    # We look for full month names followed immediately by digits
    slug_pattern = r"(january|february|march|april|may|june|july|august|september|october|november|december)-?(\d{1,2})"
    slug_match = re.search(slug_pattern, text, re.IGNORECASE)

    if slug_match:
        try:
            month_str = slug_match.group(1)
            day_int = int(slug_match.group(2))

            # Parse the month name to a number
            dt = parser.parse(f"{month_str} {day_int} {default_year}")
            return dt
        except ValueError:
            pass  # Fall through to general parser if this fails

    # --- CASE 4: General Text Parser (The Catch-All) ---
    # Matches: "December 2025", "Jan 15, 2025", "31st of Dec"
    # Logic: Finds date-like strings and parses them.
    text_pattern = r"([A-Z][a-z]{2,8}[-.\s]+(?:\d{1,2}(?:st|nd|rd|th)?[-,\s]+)?\d{4})"
    matches = re.findall(text_pattern, text)

    if matches:
        for date_str in matches:
            try:
                clean_str = date_str.replace("-", " ")
                dt = parser.parse(clean_str, fuzzy=True)

                # Fix: If "Month Year" only, default to END of month
                if re.match(
                    r"^[A-Z][a-z]{2,8}\s+\d{4}$", clean_str.strip(), re.IGNORECASE
                ):
                    _, last_day = calendar.monthrange(dt.year, dt.month)
                    dt = dt.replace(day=last_day)

                return dt  # Return the first valid high-confidence match
            except (ValueError, OverflowError):
                continue

    return None
