"""Optional UN Comtrade data. Explicit missingness if the API is unavailable.

We use annual HS 8542 (integrated circuits) imports by reporter, comparing
Taiwan ('Other Asia, nes' in some Comtrade datasets) and the US with the world.
This is a rough trade-link proxy, NOT an AI-specific trade measure.
"""
import argparse
import logging

import numpy as np
import pandas as pd
import requests

from src.settings import CONFIG, RAW

LOG = logging.getLogger(__name__)
API = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"


def import_value(reporter: int, partner: int, year: int, session: requests.Session) -> float:
    response = session.get(API, params={
        "period": year, "reporterCode": reporter, "partnerCode": partner,
        "cmdCode": "8542", "flowCode": "M", "maxRecords": 30,
    }, timeout=30)
    response.raise_for_status()
    data = response.json().get("data") or []
    # If more than one classification/aggregation level is returned, ambiguity is
    # too high: we do not sum potentially duplicated records.
    valid = [r for r in data if str(r.get("cmdCode")) == "8542" and
             str(r.get("partnerCode")) == str(partner) and
             str(r.get("flowCode")) == "M" and r.get("primaryValue") is not None]
    if len(valid) != 1:
        return float("nan")
    return float(valid[0]["primaryValue"])


def collect_trade(year: int) -> None:
    countries = pd.read_csv(CONFIG / "country_etfs.csv")
    session = requests.Session()
    session.headers.update({"User-Agent": "University economics data study"})
    rows = []
    for row in countries.itertuples():
        try:
            world = import_value(row.un_code, 0, year, session)
            # 490 is a common Comtrade 'Other Asia, nes' code (Taiwan proxy).
            taiwan = import_value(row.un_code, 490, year, session)
            us = import_value(row.un_code, 842, year, session)
            share = (taiwan + us) / world if world > 0 and np.isfinite([taiwan, us]).all() else np.nan
            if pd.notna(share) and not 0 <= share <= 1.01:
                share = np.nan
        except (requests.RequestException, ValueError, KeyError) as exc:
            LOG.warning("UN Comtrade unavailable for %s: %s", row.iso3, exc)
            world = taiwan = us = share = np.nan
        rows.append({"iso3": row.iso3, "chip_imports_world_usd": world,
                     "chip_imports_taiwan_proxy_usd": taiwan, "chip_imports_us_usd": us,
                     "chip_import_share_taiwan_us": share, "trade_year": year})
    out = pd.DataFrame(rows)
    RAW.mkdir(parents=True, exist_ok=True)
    out.to_csv(RAW / "comtrade_chips.csv", index=False)
    LOG.info("Valid trade ratios: %d/%d", out.chip_import_share_taiwan_us.notna().sum(), len(out))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2024)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    collect_trade(args.year)
