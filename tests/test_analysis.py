import numpy as np
import pandas as pd
import pytest

from src.analysis import (
    event_session, daily_returns, market_model_ar, check_events,
    sensitivity_by_stock, country_regression, pre_post_sensitivity,
)
from src.settings import Settings


def test_after_close_uses_next_trading_day_not_calendar_day():
    sessions = pd.to_datetime(["2026-11-19", "2026-11-20", "2026-11-23"])
    assert event_session("2026-11-20", sessions) == pd.Timestamp("2026-11-23")
    assert event_session("2026-11-19", sessions) == pd.Timestamp("2026-11-20")


def test_returns_do_not_fill_missing_prices():
    prices = pd.DataFrame({"A": [100, np.nan, 105], "SPY": [100, 101, 102]})
    out = daily_returns(prices)
    assert np.isnan(out.A.iloc[1])
    assert np.isnan(out.A.iloc[2])


def test_market_model_only_uses_pre_event_window():
    # R_A = 0.001 + 2*R_SPY in the estimation period; on the event day
    # it receives an additional 3 percentage points of idiosyncratic return.
    market = np.array([0.001, -.004, .003, .009, -.005, .007, -.002, .006,
                       -.004, .003, .01, .004, -.003, .002], dtype=float)
    stock = .001 + 2 * market
    stock[11] += .03
    returns = pd.DataFrame({"A": stock, "SPY": market})
    settings = Settings(estimation_start=-10, estimation_end=-3, min_estimation_days=7)
    result = market_model_ar(returns, "A", "SPY", event_pos=11, settings=settings)
    assert result is not None
    assert result["abnormal_return"] == pytest.approx(.03, abs=1e-10)
    assert result["market_beta"] == pytest.approx(2.0, abs=1e-10)


def test_event_list_rejects_duplicates_and_before_open():
    with pytest.raises(ValueError):
        check_events(pd.DataFrame({"announcement_date": ["2026-11-17", "2026-11-17"],
                                   "session": ["after_close", "after_close"]}))
    with pytest.raises(ValueError):
        check_events(pd.DataFrame({"announcement_date": ["2026-11-17"],
                                   "session": ["before_open"]}))


def test_sensitivity_slope_is_directional_response_not_market_beta():
    x = np.array([-.07, -.05, -.03, -.01, .01, .03, .05, .07])
    panel = pd.DataFrame({"ticker": "TEST", "nvda_abnormal_return": x,
                          "abnormal_return": .002 + 1.5 * x})
    result = sensitivity_by_stock(panel)
    assert result.sensitivity.iloc[0] == pytest.approx(1.5)
    assert result.intercept.iloc[0] == pytest.approx(.002)


def test_cutoff_comparison_does_not_mix_2022_earnings():
    dates = pd.to_datetime(["2022-11-16"] * 8 + ["2023-02-22"] * 8)
    x = np.tile(np.linspace(-.04, .04, 8), 2)
    panel = pd.DataFrame({"ticker": "ABC", "announcement_date": dates,
                          "nvda_abnormal_return": x, "abnormal_return": x})
    out = pre_post_sensitivity(panel, min_events=8)
    assert set(out.period) == {"Pre", "Post"}


def test_country_model_fails_closed_when_trade_data_missing():
    slopes = pd.DataFrame({"ticker": ["EWT", "EWJ"], "sensitivity": [1., .3]})
    countries = pd.DataFrame({"etf": ["EWT", "EWJ"], "iso3": ["TWN", "JPN"]})
    model, _, required = country_regression(slopes, countries)
    assert model is None
    assert "chip_import_share_taiwan_us" in required
