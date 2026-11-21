"""SEC accounting data and dated ETF holdings for firm-level labels."""
import argparse
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from src.settings import CONFIG, RAW

LOG = logging.getLogger(__name__)
SEC_TICKERS = "https://www.sec.gov/files/company_tickers.json"
SEC_FACTS = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
REVENUE_TAGS = [
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues", "SalesRevenueNet", "RevenueFromContractWithCustomerIncludingAssessedTax",
]


def sec_session() -> requests.Session:
    user_agent = os.getenv("SEC_USER_AGENT", "").strip()
    if "@" not in user_agent or len(user_agent) < 12:
        raise ValueError("Set SEC_USER_AGENT='University research your.real.email@example.com' before collecting SEC data.")
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"})
    return session


def ticker_map(session: requests.Session) -> dict[str, int]:
    path = RAW / "sec_ticker_map.json"
    if not path.exists():
        response = session.get(SEC_TICKERS, timeout=35)
        response.raise_for_status()
        path.write_text(response.text, encoding="utf-8")
    data = json.loads(path.read_text(encoding="utf-8"))
    return {item["ticker"].replace(".", "-"): int(item["cik_str"]) for item in data.values()}


def load_facts(cik: int, session: requests.Session) -> dict:
    path = RAW / "sec_facts" / f"CIK{cik:010d}.json"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        response = session.get(SEC_FACTS.format(cik=cik), timeout=35)
        response.raise_for_status()
        path.write_text(response.text, encoding="utf-8")
        time.sleep(0.15)  # keep well below the SEC's published request rate guidance
    return json.loads(path.read_text(encoding="utf-8"))


def annual_facts(facts: dict, tag: str, cutoff: str = "2022-11-29") -> pd.DataFrame:
    """Annual US-GAAP facts *filed* by cutoff, not 2026 restatements.

    `fy` from EDGAR refers to a filing year, which can include comparatives.
    We use start/end dates and a 270-380 day period instead.
    """
    series = facts.get("facts", {}).get("us-gaap", {}).get(tag, {}).get("units", {}).get("USD", [])
    if not series:
        return pd.DataFrame(columns=["start", "end", "filed", "val"])
    df = pd.DataFrame(series)
    if not {"start", "end", "filed", "val", "form"}.issubset(df):
        return pd.DataFrame(columns=["start", "end", "filed", "val"])
    for col in ["start", "end", "filed"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    cutoff_date = pd.Timestamp(cutoff)
    duration = (df["end"] - df["start"]).dt.days
    df = df[(df["form"].isin(["10-K", "10-K/A"])) & (duration.between(270, 380)) &
            (df["end"] <= cutoff_date) & (df["filed"] <= cutoff_date)]
    return df.sort_values(["end", "filed"]).drop_duplicates(["start", "end"], keep="first")


def rd_over_revenue(facts: dict, cutoff: str = "2022-11-29") -> tuple[float, str | None]:
    """Latest annual R&D / revenue observable *before* the stated cutoff."""
    research = annual_facts(facts, "ResearchAndDevelopmentExpense", cutoff)
    if research.empty:
        return float("nan"), None
    for row in research.sort_values("end", ascending=False).itertuples():
        for revenue_tag in REVENUE_TAGS:
            revenue = annual_facts(facts, revenue_tag, cutoff)
            matched = revenue[(revenue["start"] == row.start) & (revenue["end"] == row.end)]
            if not matched.empty:
                revenue_value = float(matched.iloc[0]["val"])
                if revenue_value > 0 and row.val >= 0:
                    return float(row.val / revenue_value), row.end.strftime("%Y-%m-%d")
    return float("nan"), None


def parse_issuer_holdings(path: Path) -> set[str]:
    """Extract symbols from a *real* holdings CSV, including issuer preambles."""
    contents = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    for skiprows in range(min(35, len(contents))):
        line = contents[skiprows].strip().lower()
        if not re.search(r"(^|,|;)\s*\"?(ticker|symbol|ticker symbol)\"?\s*(,|;|$)", line):
            continue
        try:
            holdings = pd.read_csv(path, skiprows=skiprows)
            col = next((col for col in holdings if str(col).strip().lower() in
                        {"ticker", "symbol", "ticker symbol"}), None)
            if col is None:
                continue
            tickers = holdings[col].dropna().astype(str).str.strip().str.upper()
            return set(tickers[tickers.str.fullmatch(r"[A-Z][A-Z0-9.\-]{0,8}")].str.replace(".", "-", regex=False))
        except (pd.errors.ParserError, UnicodeDecodeError):
            continue
    raise ValueError(f"Could not recognize a ticker column in {path}. Open the issuer CSV and inspect its header.")


def holdings_labels(tickers: pd.Series) -> pd.DataFrame:
    files = sorted((CONFIG / "holdings").glob("*.csv"))
    labels = pd.DataFrame({"ticker": tickers})
    if not files:
        labels["ai_etf_member"] = np.nan
        labels["semi_etf_member"] = np.nan
        return labels
    etf_members = {"BOTZ": set(), "ARTY": set(), "SOXX": set()}
    present = set()
    for path in files:
        issuer = path.name.split("_")[0].upper()
        if issuer in etf_members:
            etf_members[issuer].update(parse_issuer_holdings(path))
            present.add(issuer)
    ai_available = "BOTZ" in present or "ARTY" in present
    labels["ai_etf_member"] = labels.ticker.isin(etf_members["BOTZ"] | etf_members["ARTY"]).astype(float) if ai_available else np.nan
    labels["semi_etf_member"] = labels.ticker.isin(etf_members["SOXX"]).astype(float) if "SOXX" in present else np.nan
    return labels


def collect_firm_labels(market_caps: bool = False) -> None:
    meta_file = RAW / "nasdaq100_constituents.csv"
    if not meta_file.exists():
        raise FileNotFoundError("First run: python -m src.collect")
    firms = pd.read_csv(meta_file)
    firms["technology_label"] = firms["sector"].str.contains("technology", case=False, na=False).astype(int)
    firms["semiconductor_label"] = firms["subsector"].str.contains("semiconductor", case=False, na=False).astype(int)
    session = sec_session()
    mapping = ticker_map(session)
    results = []
    for i, row in enumerate(firms.itertuples(), start=1):
        cik = mapping.get(row.ticker)
        ratio, end_date = float("nan"), None
        if cik is not None:
            try:
                ratio, end_date = rd_over_revenue(load_facts(cik, session))
            except (requests.RequestException, ValueError, KeyError) as exc:
                LOG.warning("SEC facts missing for %s: %s", row.ticker, exc)
        results.append({"ticker": row.ticker, "rd_revenue": ratio, "rd_fiscal_end": end_date, "cik": cik})
        if i % 15 == 0:
            LOG.info("Processed %d/%d firm filings", i, len(firms))
    firms = firms.merge(pd.DataFrame(results), on="ticker", how="left", validate="one_to_one")
    firms = firms.merge(holdings_labels(firms.ticker), on="ticker", how="left", validate="one_to_one")
    firms["market_cap_usd"] = np.nan
    if market_caps:
        import yfinance as yf
        for idx, ticker in firms.ticker.items():
            try:
                cap = yf.Ticker(ticker).fast_info.market_cap
                firms.loc[idx, "market_cap_usd"] = float(cap) if cap is not None else np.nan
            except (KeyError, ValueError, TypeError, AttributeError) as exc:
                LOG.warning("Market cap missing for %s: %s", ticker, exc)
    firms["size_snapshot_utc"] = datetime.now(timezone.utc).date().isoformat() if market_caps else None
    firms.to_csv(RAW / "firm_labels.csv", index=False)
    LOG.info("Saved firm_labels.csv. R&D available: %d/%d", firms.rd_revenue.notna().sum(), len(firms))


def main():
    parser = argparse.ArgumentParser(description="Collect SEC research spending and ETF labels")
    parser.add_argument("--market-caps", action="store_true", help="Add current market cap snapshots (slow, look-ahead bias)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    collect_firm_labels(market_caps=args.market_caps)


if __name__ == "__main__":
    main()
