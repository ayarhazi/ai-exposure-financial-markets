"""Optional broader-universe robustness exercise (current S&P 500 members).

Run explicitly, as the extra downloads are sizeable and can be rate-limited.
"""
import argparse
from io import StringIO

import pandas as pd
import requests

from src.collect import get_prices, save_csv
from src.settings import RAW, Settings

URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def sp500_members() -> pd.DataFrame:
    response = requests.get(URL, headers={"User-Agent": "University data science project"}, timeout=30)
    response.raise_for_status()
    for table in pd.read_html(StringIO(response.text)):
        if "Symbol" in table and "Security" in table and len(table) > 450:
            return pd.DataFrame({
                "ticker": table["Symbol"].astype(str).str.replace(".", "-", regex=False),
                "company": table["Security"],
                "sector": table["GICS Sector"] if "GICS Sector" in table else "Unknown",
            })
    raise ValueError("The source table changed; inspect the Wikipedia S&P 500 page.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    members_path = RAW / "sp500_constituents.csv"
    prices_path = RAW / "sp500_prices.csv"
    if args.refresh or not members_path.exists():
        members = sp500_members()
        save_csv(members, members_path)
    else:
        members = pd.read_csv(members_path)
    if args.refresh or not prices_path.exists():
        settings = Settings()
        prices = get_prices(sorted(set(members.ticker) | {"NVDA", "SPY"}),
                            settings.price_start, settings.price_end, chunk_size=25)
        save_csv(prices.rename_axis("date").reset_index(), prices_path)
    print("Optional S&P 500 data ready; rerun the notebook to see the extension.")


if __name__ == "__main__":
    main()
