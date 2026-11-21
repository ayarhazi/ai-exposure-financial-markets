import numpy as np
import pandas as pd
import pytest

from src.firm_data import annual_facts, rd_over_revenue, parse_issuer_holdings


def test_annual_facts_reject_late_filing():
    facts = {"facts": {"us-gaap": {"ResearchAndDevelopmentExpense": {
        "units": {"USD": [
            {"start": "2020-01-01", "end": "2020-12-31", "filed": "2021-02-05", "form": "10-K", "val": 30},
            {"start": "2021-01-01", "end": "2021-12-31", "filed": "2023-01-05", "form": "10-K", "val": 45},
        ]}}}}}
    out = annual_facts(facts, "ResearchAndDevelopmentExpense", cutoff="2022-11-29")
    assert len(out) == 1
    assert out.val.iloc[0] == 30


def test_rd_ratio_matching_annual_dates():
    research = [{"start": "2021-01-01", "end": "2021-12-31", "filed": "2022-02-10", "form": "10-K", "val": 20}]
    revenues = [{"start": "2021-01-01", "end": "2021-12-31", "filed": "2022-02-10", "form": "10-K", "val": 200}]
    facts = {"facts": {"us-gaap": {
        "ResearchAndDevelopmentExpense": {"units": {"USD": research}},
        "Revenues": {"units": {"USD": revenues}},
    }}}
    ratio, date = rd_over_revenue(facts)
    assert ratio == pytest.approx(.1)
    assert date == "2021-12-31"


def test_holdings_csv_with_issuer_preamble(tmp_path):
    path = tmp_path / "BOTZ_2026-11-20.csv"
    path.write_text("Global X ETF holdings\nAs of 2026-11-20\nTicker,Name,Weight\nNVDA,Nvidia,7.0\nAAPL,Apple,1.0\n")
    assert parse_issuer_holdings(path) == {"NVDA", "AAPL"}
