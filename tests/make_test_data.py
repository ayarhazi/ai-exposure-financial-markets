"""Generate FAKE data solely for execution tests, never for research conclusions.

Usage: python -m tests.make_test_data /tmp/nvda_fixture
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd

from src.settings import CONFIG


def generate(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2017-01-02", "2026-11-20")
    events = pd.read_csv(CONFIG / "earnings_nvda.csv")
    positions = set()
    for release in pd.to_datetime(events.announcement_date):
        pos = dates.searchsorted(release, side="right")
        if pos < len(dates):
            positions.add(pos)
    n = len(dates)
    benchmark = rng.normal(.0003, .008, n)
    shocks = np.zeros(n)
    for position in positions:
        shocks[position] = rng.normal(0, .08)
    result = {"SPY": 100 * np.cumprod(1 + benchmark),
              "QQQ": 100 * np.cumprod(1 + 1.25*benchmark + rng.normal(0, .004, n)),
              "NVDA": 100 * np.cumprod(1 + 1.5*benchmark + shocks + rng.normal(0, .009, n))}
    firms = []
    for i in range(24):
        ticker = f"FAKE{i:02d}"
        result[ticker] = 100 * np.cumprod(1 + (0.7+i*.02)*benchmark +
                                           (0.1 + i*.055)*shocks + rng.normal(0, .012, n))
        firms.append({"ticker": ticker, "company": f"Synthetic firm {i}",
                      "sector": "Technology" if i % 2 else "Industrials",
                      "subsector": "Semiconductors" if i % 4 == 0 else "Consumer services",
                      "technology_label": int(i % 2 == 1),
                      "semiconductor_label": int(i % 4 == 0),
                      "rd_revenue": i / 100,
                      "ai_etf_member": int(i % 3 == 0),
                      "semi_etf_member": int(i % 4 == 0),
                      "market_cap_usd": float(1e10 * (i + 1))})
    pd.DataFrame(result, index=dates).rename_axis("date").to_csv(folder / "us_prices.csv")
    pd.DataFrame(firms)[["ticker", "company", "sector", "subsector"]].to_csv(folder / "nasdaq100_constituents.csv", index=False)
    pd.DataFrame(firms).to_csv(folder / "firm_labels.csv", index=False)
    countries = pd.read_csv(CONFIG / "country_etfs.csv")
    country_data = {}
    for i, ticker in enumerate(countries.etf):
        returns = (0.5 + i*.01)*benchmark + (.1 + i*.025)*shocks + rng.normal(0, .01, n)
        country_data[ticker] = 100 * np.cumprod(1 + returns)
    pd.DataFrame(country_data, index=dates).rename_axis("date").to_csv(folder / "country_etf_prices.csv")
    print("TEST-ONLY synthetic fixture:", folder)


if __name__ == "__main__":
    generate(Path(sys.argv[1]))
