"""Collect and save the financial data used in our project.
This script downloads stock prices, Nasdaq-100 company information
and World Bank GDP data. We save the datasets locally so we can
reuse them without downloading everything each time.
"""
import argparse
import json
import logging
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

from src.settings import CONFIG, RAW, Settings

LOG = logging.getLogger(__name__)
WIKI_URL = "https://en.wikipedia.org/wiki/List_of_NASDAQ-100_companies"


def get_constituents() -> pd.DataFrame:
    """Current Nasdaq-100 snapshot. Wikipedia uses ICB, not GICS, sectors."""
    response = requests.get(WIKI_URL, headers={"User-Agent": "University research project (educational)"}, timeout=40)
    response.raise_for_status()
    tables = pd.read_html(StringIO(response.text))
    for table in tables:
        table.columns = [" ".join(map(str, c)) if isinstance(c, tuple) else str(c) for c in table.columns]
        columns = {col: col.lower() for col in table.columns}
        ticker_col = next((c for c in table if "ticker" in columns[c]), None)
        company_col = next((c for c in table if "company" in columns[c]), None)
        if not ticker_col or not company_col or len(table) < 70:
            continue
        industry_col = next((c for c in table if "icb industry" in columns[c]), None)
        sub_col = next((c for c in table if "icb subsector" in columns[c]), None)
        out = pd.DataFrame({
            "ticker": table[ticker_col].astype(str).str.strip().str.replace(".", "-", regex=False),
            "company": table[company_col].astype(str).str.strip(),
            "sector": table[industry_col].astype(str) if industry_col else "Unknown",
            "subsector": table[sub_col].astype(str) if sub_col else "Unknown",
        })
        out = out.drop_duplicates("ticker")
        out = out[out.ticker.str.fullmatch(r"[A-Z][A-Z0-9-]*")]
        if len(out) >= 70:
            return out.reset_index(drop=True)
    raise ValueError("The Nasdaq-100 table structure changed; inspect Wikipedia and update get_constituents().")


def get_prices(tickers: list[str], start: str, end: str, chunk_size: int = 30) -> pd.DataFrame:
    """Adjusted daily close prices with dates on a common US exchange calendar.

    Individual failures are logged; missing tickers remain missing, not zero.
    """
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("Install requirements.txt, including yfinance.") from exc

    chunks = []
    for start_at in range(0, len(tickers), chunk_size):
        group = tickers[start_at:start_at + chunk_size]
        LOG.info("Downloading tickers %d-%d of %d", start_at + 1, min(start_at + len(group), len(tickers)), len(tickers))
        data = yf.download(group, start=start, end=end, auto_adjust=True, progress=False,
                           threads=False, group_by="column", timeout=25)
        if data.empty:
            LOG.warning("No prices returned for %s", group)
            continue
        if isinstance(data.columns, pd.MultiIndex):
            close = data["Close"].copy()
        else:
            close = data[["Close"]].rename(columns={"Close": group[0]})
        close = close.reindex(columns=group)
        chunks.append(close)
    if not chunks:
        raise RuntimeError("No prices were downloaded. Check the network or Yahoo rate limits.")
    prices = pd.concat(chunks, axis=1).loc[:, lambda x: ~x.columns.duplicated()]
    prices.index = pd.DatetimeIndex(prices.index).tz_localize(None).normalize()
    prices = prices.sort_index().apply(pd.to_numeric, errors="coerce")
    prices = prices.mask(prices <= 0)
    return prices


def get_world_bank_gdp(countries: pd.DataFrame, year: int = 2024) -> pd.DataFrame:
    """Last available GDP in current USD up to the requested year.

    Taiwan, for example, is not separately reported in the World Bank API.
    """
    rows = []
    session = requests.Session()
    for row in countries.itertuples():
        try:
            response = session.get(
                f"https://api.worldbank.org/v2/country/{row.wb_code}/indicator/NY.GDP.MKTP.CD",
                params={"format": "json", "date": f"{year-2}:{year}", "per_page": 20}, timeout=20)
            response.raise_for_status()
            payload = response.json()
            observations = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
            usable = [x for x in (observations or []) if x.get("value") is not None]
            value = float(usable[0]["value"]) if usable else float("nan")
            data_year = int(usable[0]["date"]) if usable else None
        except (requests.RequestException, ValueError, KeyError, TypeError, IndexError) as exc:
            LOG.warning("World Bank unavailable for %s: %s", row.iso3, exc)
            value, data_year = float("nan"), None
        rows.append({"iso3": row.iso3, "gdp_usd": value, "gdp_year": data_year})
    return pd.DataFrame(rows)


def save_csv(data: pd.DataFrame, path: Path, index: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=index)
    LOG.info("Saved %s (%d rows)", path.relative_to(RAW.parent.parent), len(data))


def collect(refresh: bool = False) -> None:
    """Acquire several independent, dated source snapshots."""
    RAW.mkdir(parents=True, exist_ok=True)
    settings = Settings()
    country_list = pd.read_csv(CONFIG / "country_etfs.csv")
    metadata = RAW / "nasdaq100_constituents.csv"
    prices_file = RAW / "us_prices.csv"
    country_file = RAW / "country_etf_prices.csv"
    gdp_file = RAW / "world_bank_gdp.csv"
    if refresh or not metadata.exists():
        constituents = get_constituents()
        save_csv(constituents, metadata)
    else:
        constituents = pd.read_csv(metadata)

    if refresh or not prices_file.exists():
        tickers = sorted(set(constituents.ticker) | {"NVDA", "SPY", "QQQ"})
        us_prices = get_prices(tickers, settings.price_start, settings.price_end)
        save_csv(us_prices.rename_axis("date").reset_index(), prices_file)
    if refresh or not country_file.exists():
        country_prices = get_prices(country_list.etf.tolist(), settings.price_start, settings.price_end)
        save_csv(country_prices.rename_axis("date").reset_index(), country_file)
    if refresh or not gdp_file.exists():
        save_csv(get_world_bank_gdp(country_list), gdp_file)

    manifest = {
        "collection_utc": datetime.now(timezone.utc).isoformat(),
        "price_start": settings.price_start,
        "price_end_exclusive": settings.price_end,
        "prices": "Yahoo Finance / yfinance; auto_adjust=True",
        "universe": WIKI_URL,
        "country_etfs": "config/country_etfs.csv (US-listed ETFs, not local closes)",
        "gdp": "https://api.worldbank.org/v2/country/{code}/indicator/NY.GDP.MKTP.CD",
        "note": "Preserve raw CSV and manifest to reproduce the exact results, even if the live sources change.",
    }
    (RAW / "collection_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    LOG.info("Initial collection complete. Run the notebook next.")


def main():
    parser = argparse.ArgumentParser(description="Collect datasets for Nvidia AI event study")
    parser.add_argument("--refresh", action="store_true", help="Overwrite all locally cached raw files")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    collect(refresh=args.refresh)


if __name__ == "__main__":
    main()
