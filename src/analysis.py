"""Functions for analyzing stock-market reactions to Nvidia's earnings.
This file contains the calculations for returns, event studies,
regressions and comparisons between companies and time periods.
We express returns as decimals (for example: 0.01 means 1%).
"""

from __future__ import annotations
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.decomposition import PCA
from src.settings import Settings

def load_prices(path) -> pd.DataFrame:
    data = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    if data.index.has_duplicates:
        raise ValueError(f"Repeated dates in {path}")
    return data.apply(pd.to_numeric, errors="coerce").mask(lambda x: x <= 0)


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Do not forward-fill delisted or missing price observations."""
    return prices.pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan)


def check_events(events: pd.DataFrame) -> pd.DataFrame:
    events = events.copy()
    events["announcement_date"] = pd.to_datetime(events["announcement_date"])
    if events.announcement_date.duplicated().any():
        raise ValueError("Duplicate Nvidia announcement date in the event file")
    if not events.session.eq("after_close").all():
        raise ValueError("This pipeline only implements AFTER-CLOSE releases")
    return events.sort_values("announcement_date").reset_index(drop=True)


def event_session(announcement, us_sessions: pd.DatetimeIndex) -> pd.Timestamp | None:
    """First US trading session STRICTLY after an after-close announcement."""
    release_day = pd.Timestamp(announcement).normalize()
    position = us_sessions.searchsorted(release_day, side="right")
    return us_sessions[position] if position < len(us_sessions) else None


def market_model_ar(returns: pd.DataFrame, ticker: str, benchmark: str,
                    event_pos: int, window: tuple[int, int] = (0, 0),
                    settings: Settings | None = None) -> dict | None:
    """Out-of-sample cumulative abnormal return using a pre-event market model.

    Estimation days are [-250,-30] relative to the post-announcement session.
    Window [0,1] includes the first and second post-announcement returns.
    """
    s = settings or Settings()
    if ticker not in returns or benchmark not in returns or ticker == benchmark:
        return None
    left = event_pos + s.estimation_start
    right = event_pos + s.estimation_end
    first, last = event_pos + window[0], event_pos + window[1]

    if left < 0 or right >= event_pos or first < 0 or last >= len(returns) or first > last:
        return None
    history = returns.iloc[left:right + 1][[ticker, benchmark]].dropna()
    if len(history) < s.min_estimation_days:
        return None
    
    x = history[benchmark].to_numpy(dtype=float)
    y = history[ticker].to_numpy(dtype=float)
    variance = np.var(x)

    if variance < 1e-12:
        return None
    beta = float(np.cov(x, y, ddof=0)[0, 1] / variance)
    alpha = float(np.mean(y) - beta * np.mean(x))
    observed = returns.iloc[first:last + 1][[ticker, benchmark]]
    
    if observed.isna().any().any():
        return None
    residual = observed[ticker] - alpha - beta * observed[benchmark]
    return {
        "abnormal_return": float(residual.sum()),
        "raw_return": float(observed[ticker].sum()),
        "benchmark_return": float(observed[benchmark].sum()),
        "market_beta": beta,
        "n_estimation": len(history),
    }


def event_study(prices: pd.DataFrame, events: pd.DataFrame,
                tickers: list[str] | None = None, benchmark: str = "SPY",
                window: tuple[int, int] = (0, 0),
                settings: Settings | None = None) -> pd.DataFrame:
    """For every announcement, calculate each stock's abnormal next-session return.

    Each release is aligned to the benchmark's ACTUAL trading dates. ETFs in
    the country analysis are US-listed, and therefore use this US timetable.
    """
    s = settings or Settings()
    events = check_events(events)

    if benchmark not in prices:
        raise ValueError(f"Benchmark {benchmark} is not in the price table")
    
    us_sessions = prices.index[prices[benchmark].notna()]
    aligned = prices.reindex(us_sessions)
    returns = daily_returns(aligned)

    if tickers is None:
        tickers = [col for col in prices if col != benchmark]
    rows = []

    for event in events.itertuples():
        date = event_session(event.announcement_date, us_sessions)
        if date is None:
            continue
        position = us_sessions.get_loc(date)
        for ticker in tickers:
            ar = market_model_ar(returns, ticker, benchmark, position, window, s)
            if ar is None:
                continue
            rows.append({"ticker": ticker, "announcement_date": event.announcement_date,
                         "event_date": date, "window": f"[{window[0]},{window[1]}]", **ar})
            
    return pd.DataFrame(rows, columns=[
        "ticker", "announcement_date", "event_date", "window", "abnormal_return",
        "raw_return", "benchmark_return", "market_beta", "n_estimation",
    ])


def attach_nvda_shocks(event_results: pd.DataFrame) -> pd.DataFrame:
    """Merge by announcement, not by a possibly repeated return date."""
    nvidia = event_results.loc[event_results.ticker.eq("NVDA"),
                               ["announcement_date", "abnormal_return"]]
    nvidia = nvidia.rename(columns={"abnormal_return": "nvda_abnormal_return"})
    return (event_results[event_results.ticker.ne("NVDA")]
            .merge(nvidia, on="announcement_date", how="inner", validate="many_to_one"))


def sensitivity_by_stock(event_panel: pd.DataFrame, min_events: int = 8) -> pd.DataFrame:
    """OLS slope of each asset's event AR on Nvidia's event AR, with intercept."""
    rows = []

    for ticker, group in event_panel.groupby("ticker"):
        group = group[["nvda_abnormal_return", "abnormal_return"]].dropna()
        if len(group) < min_events or group.nvda_abnormal_return.var() < 1e-12:
            continue
        reg = stats.linregress(group.nvda_abnormal_return, group.abnormal_return)

        rows.append({"ticker": ticker, "sensitivity": reg.slope,
                     "intercept": reg.intercept, "r": reg.rvalue,
                     "p_value": reg.pvalue, "std_error": reg.stderr,
                     "n_events": len(group)})
        
    return pd.DataFrame(rows, columns=["ticker", "sensitivity", "intercept", "r", "p_value", "std_error", "n_events"])


def pre_post_sensitivity(event_panel: pd.DataFrame, cutoff="2022-11-30",
                         min_events=8) -> pd.DataFrame:
    panel = event_panel.copy()
    panel["period"] = np.where(panel.announcement_date < pd.Timestamp(cutoff), "Pre", "Post")
    frames = []

    for period, group in panel.groupby("period"):
        result = sensitivity_by_stock(group, min_events)
        result["period"] = period
        frames.append(result)

    if not frames:
        return pd.DataFrame()
    
    return pd.concat(frames, ignore_index=True)




def market_betas_before_cutoff(prices: pd.DataFrame, cutoff="2022-11-30", benchmark="SPY") -> pd.DataFrame:
    """A historical overall-market beta, distinct from event-day sensitivity."""
    subset = daily_returns(prices.loc[prices.index < pd.Timestamp(cutoff)])
    rows = []

    for ticker in subset.columns:
        if ticker == benchmark:
            continue
        pair = subset[[ticker, benchmark]].dropna()
        if len(pair) < 180 or pair[benchmark].var() < 1e-12:
            beta = np.nan
        else:
            beta = pair[ticker].cov(pair[benchmark]) / pair[benchmark].var()
        rows.append({"ticker": ticker, "historical_market_beta": beta})

    return pd.DataFrame(rows)


def cross_section_regression(sensitivities: pd.DataFrame, labels: pd.DataFrame):
    """Explanatory association, not causal inference; HC3 standard errors.

    Only include columns with meaningful coverage and variation. Report which
    covariates are actually estimated, rather than pretending all are present.
    """
    merged = sensitivities.merge(labels, on="ticker", how="left", validate="one_to_one")

    if "market_cap_usd" in merged:
        merged["log_market_cap"] = np.log(merged["market_cap_usd"].where(merged.market_cap_usd > 0))

    chosen = []

    for col in ["semiconductor_label", "technology_label", "rd_revenue", "ai_etf_member",
                "semi_etf_member", "log_market_cap", "historical_market_beta"]:
        if col in merged and merged[col].notna().sum() >= max(20, int(0.55 * len(merged))) and merged[col].nunique(dropna=True) > 1:
            chosen.append(col)

    if not chosen:
        return None, merged, []
    
    sample = merged.dropna(subset=["sensitivity"] + chosen)

    if len(sample) < max(25, 5 * (len(chosen) + 1)):
        # Small sample: use the most robust available non-missing controls.
        chosen = [c for c in ["semiconductor_label", "technology_label", "historical_market_beta"]
                  if c in chosen]
        sample = merged.dropna(subset=["sensitivity"] + chosen)

    if len(sample) < max(15, 4 * (len(chosen) + 1)) or not chosen:
        return None, merged, chosen
    
    X = sm.add_constant(sample[chosen].astype(float), has_constant="add")

    if np.linalg.matrix_rank(X.to_numpy()) < X.shape[1]:
        return None, merged, chosen
    
    model = sm.OLS(sample.sensitivity, X).fit(cov_type="HC3")
    return model, sample, chosen


def country_regression(sensitivity: pd.DataFrame, countries: pd.DataFrame):
    """Run H4 ONLY if both actual tech weights and trade measures exist.

    Never fill an unobserved trade link or tech weight with a guess/zero.
    """
    merged = sensitivity.merge(countries, left_on="ticker", right_on="etf", validate="one_to_one")
    required = ["tech_weight", "chip_import_share_taiwan_us"]

    if not all(col in merged for col in required):
        return None, merged, required
    
    data = merged.dropna(subset=required + ["sensitivity"])

    if len(data) < 12:
        return None, merged, required
    
    X = sm.add_constant(data[required], has_constant="add")
    if np.linalg.matrix_rank(X.to_numpy()) < X.shape[1]:
        return None, merged, required
    
    model = sm.OLS(data.sensitivity, X).fit(cov_type="HC3")
    return model, data, required


def yearly_pca(prices: pd.DataFrame, tickers: list[str], min_stocks: int = 12) -> pd.DataFrame:
    """Descriptive PCA of standardized daily returns, year by year."""

    returns = daily_returns(prices[[t for t in tickers if t in prices]])
    rows = []

    for year, sample in returns.groupby(returns.index.year):
        if year < 2018 or len(sample) < 120:
            continue
        coverage = sample.notna().mean()
        keep = coverage[coverage >= 0.90].index
        
        if len(keep) < min_stocks:
            continue
        sample = sample[keep]
        deviation = sample.std(ddof=0)
        sample = sample.loc[:, deviation > 1e-8]

        if sample.shape[1] < min_stocks:
            continue

        # Remaining gaps (<10% per ticker) are imputed with their within-year mean,
        # after excluding poorly covered stocks. This is documented as a limitation.

        standardized = (sample - sample.mean()) / sample.std(ddof=0)
        standardized = standardized.fillna(0)
        pca = PCA(n_components=1).fit(standardized)

        rows.append({"year": year, "pc1_variance_share": float(pca.explained_variance_ratio_[0]),
                     "n_stocks": standardized.shape[1], "n_days": standardized.shape[0]})
    return pd.DataFrame(rows)


def placebo_nvda_shocks(prices: pd.DataFrame, events: pd.DataFrame,
                         n_placebos: int = 200, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Compare earnings-day Nvidia shocks with random non-event US trading days.

    This tests whether Nvidia itself moves unusually around earnings, rather
    than claiming that all stock-to-stock co-movement is causal spillover.
    """
    dates = prices.index[prices.SPY.notna()]
    returns = daily_returns(prices.reindex(dates))

    actual_pos = [dates.get_loc(d) for d in
                  [event_session(d, dates) for d in check_events(events).announcement_date]
                  if d is not None]
    
    actual = [market_model_ar(returns, "NVDA", "SPY", pos) for pos in actual_pos]
    actual_values = np.array([r["abnormal_return"] for r in actual if r is not None])
    excluded = set()

    for p in actual_pos:
        excluded.update(range(p - 10, p + 11))
    candidates = [p for p in range(255, len(dates)) if p not in excluded]

    if len(candidates) == 0:
        return actual_values, np.array([])
    
    rng = np.random.default_rng(seed)
    selected = rng.choice(candidates, min(n_placebos, len(candidates)), replace=False)
    placebos = [market_model_ar(returns, "NVDA", "SPY", int(p)) for p in selected]
    placebo_values = np.array([r["abnormal_return"] for r in placebos if r is not None])

    return actual_values, placebo_values


def data_quality(prices: pd.DataFrame, events: pd.DataFrame, benchmark="SPY") -> dict:
    first = pd.Timestamp(events.announcement_date.min())
    window = prices.loc[prices.index >= first]
    
    return {
        "assets": len(prices.columns),
        "trading_days": len(window),
        "announcement_dates": len(events),
        "price_observations_missing_pct": float(100 * window.isna().mean().mean()),
        "stocks_with_80pct_coverage": int((window.notna().mean() >= .8).sum()),
        "benchmark_missing_pct": float(100 * window[benchmark].isna().mean()),
    }
